import re
import hashlib
import sys
import time

import allure
import pytest
import tempfile
import os
import shutil
from pathlib import Path

from pytest_base_url.plugin import base_url
from slugify import slugify
from playwright.sync_api import Browser, BrowserContext, expect, Playwright, Page, Error, sync_playwright
from pytest_playwright.pytest_playwright import CreateContextCallback
from utils.global_map import GlobalMap
from utils import path
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Protocol,
    Sequence,
    Union,
    Pattern,
    cast,
)
from playwright._impl._locator import Locator as LocatorImpl
from playwright._impl._sync_base import mapping
from playwright.sync_api._generated import Locator as _Locator
import json
from allure import step

api_count_list = []
time_out = 0

@pytest.fixture(scope='session', autouse=True)
def test_init(base_url):
    GlobalMap.set("base_url", base_url)
    env = re.search("(https://)(.*)(.com)", base_url).group(2)
    GlobalMap.set("env", env)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, pytestconfig: Any):
    width, height = pytestconfig.getoption("--viewport")
    return {
        **browser_context_args,
        "viewport": {
            "width": width,
            "height": height,
        },
        "record_video_size": {
            "width": width,
            "height": height,
        },
    }


def pytest_addoption(parser: Any) -> None:
    group = parser.getgroup("playwright", "Playwright")
    group.addoption(
        "--viewport",
        action="store",
        default=[1440, 900],
        help="viewport size set",
        type=int,
        nargs=2
    )
    group.addoption(
        "--ui-timeout",
        default=30_000,
        help="locator timeout and expect timeout",
    )
    group.addoption(
        "--rerun_strategy",
        action="store",
        default=None,
        # 这里不使用nargs=“*”是因为无限个args对参数位置有要求，或者测试目标需要用参数指定
        help="testcase rerun strategy set, eg: screenshot=retain-on-failure,video=retain-on-failure,tracing=retain-on-failure",
    )
    group.addoption(
        "--allure_report_auto_open",
        action="store",
        default="off",
        choices=["off", "on"],
        help="if finish test, allure report auto open",
    )

@pytest.fixture(scope="session")
def ui_timeout(pytestconfig):
    timeout = pytestconfig.getoption("--ui-timeout")
    expect.set_options(timeout=timeout)
    return timeout

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    report = outcome.get_result()
    if report.failed:
        try:
            for content in item.funcargs['browser'].contexts:
                for page in content.pages:
                    if page.is_closed():
                        continue
                    bytes_png = page.screenshot(timeout=5_000, full_page=True)
                    allure.attach(bytes_png, f'失败截图---{page.title}')
        except:
            ...
@pytest.fixture
def new_context(
    browser: Browser,
    browser_context_args: Dict,
    _artifacts_recorder: "ArtifactsRecorder",
    request: pytest.FixtureRequest,
    ui_timeout: float,
    pytestconfig: Any,
    _pw_artifacts_folder: tempfile.TemporaryDirectory,
) -> Generator[CreateContextCallback, None, None]:
    browser_context_args = browser_context_args.copy()
    context_args_marker = next(request.node.iter_markers("browser_context_args"), None)
    additional_context_args = context_args_marker.kwargs if context_args_marker else {}
    browser_context_args.update(additional_context_args)
    contexts: List[BrowserContext] = []

    def _new_context(**kwargs: Any) -> BrowserContext:
        browser_context_args_copy = browser_context_args.copy()
        # 获取重试的log策略并转成列表
        _rerun_strategy = pytestconfig.getoption("--rerun_strategy").split(",")
        # 获取重试次数，此处为2则为重试两次，加上第一次，一共跑三次
        _reruns = pytestconfig.getoption("--reruns")
        video_option = pytestconfig.getoption("--video")
        # 重试log策略（默认为None）和重试次数（默认为0）参数必须都有值
        if _rerun_strategy and _reruns:
            # 使用空字符串去补足轮次和策略的对应关系
            if _reruns + 1 > len(_rerun_strategy):
                _init_rerun_strategy = [""] * (1 + _reruns - len(_rerun_strategy)) + _rerun_strategy
            # 使用切片来处理多余的策略（如果相等，则切片是本身），钶根据自身设计改成从后往前切
            else:
                _init_rerun_strategy = _rerun_strategy[:_reruns + 1]
            # 这里减1是因为request.node.execution_count从1开始，我门取列表下表是从0开始
            rerun_round = request.node.execution_count - 1
            _round_rerun_strategy = _init_rerun_strategy[rerun_round]

            # 这里先判断是否有log策略
            if _round_rerun_strategy:
                if "video" in _round_rerun_strategy:
                    video_option = _round_rerun_strategy.split("=")[-1]
                else:
                    video_option = "off"
            else:
                video_option = "off"
        # 这里只判断了video，是因为创建context时必须设置record_video_dir后才开始主动录屏
        capture_video = video_option in ["on", "retain-on-failure"]
        browser_context_args_copy.update(kwargs)
        if capture_video:
            video_option_dict = {"record_video_dir": _pw_artifacts_folder.name}
            browser_context_args_copy.update(video_option_dict)

        my_context = browser.new_context(**browser_context_args_copy)
        my_context.set_default_timeout(ui_timeout)
        my_context.set_default_navigation_timeout(ui_timeout * 2)
        original_close = my_context.close

        def _close_wrapper(*args: Any, **my_kwargs: Any) -> None:
            contexts.remove(my_context)
            _artifacts_recorder.on_will_close_browser_context(my_context)
            original_close(*args, **my_kwargs)

        my_context.close = _close_wrapper
        contexts.append(my_context)
        _artifacts_recorder.on_did_create_browser_context(my_context)
        return my_context

    yield cast(CreateContextCallback, _new_context)
    for context in contexts.copy():
        context.close()


def truncate_file_name(file_name: str) -> str:
    if len(file_name) < 256:
        return file_name
    return f"{file_name[:100]}-{hashlib.sha256(file_name.encode()).hexdigest()[:7]}-{file_name[-100:]}"

def _build_artifact_test_folder(
    pytestconfig: Any, request: pytest.FixtureRequest, folder_or_file_name: str
) -> str:
    output_dir = pytestconfig.getoption("--output")
    return os.path.join(
        output_dir,
        truncate_file_name(slugify(request.node.nodeid)),
        truncate_file_name(folder_or_file_name),
    )

class ArtifactsRecorder:
    def __init__(
        self,
        pytestconfig: Any,
        request: pytest.FixtureRequest,
        playwright: Playwright,
        pw_artifacts_folder: tempfile.TemporaryDirectory,
    ) -> None:
        self._request = request
        self._pytestconfig = pytestconfig
        self._playwright = playwright
        self._pw_artifacts_folder = pw_artifacts_folder

        self._all_pages: List[Page] = []
        self._screenshots: List[str] = []
        self._traces: List[str] = []
        self._rerun_strategy = pytestconfig.getoption("--rerun_strategy").split(",")
        self._reruns = pytestconfig.getoption("--reruns")
        if self._rerun_strategy and self._reruns:
            if self._reruns + 1 >= len(self._rerun_strategy):
                self._init_rerun_strategy = [""] * (1 + self._reruns - len(self._rerun_strategy)) + self._rerun_strategy
            else:
                self._init_rerun_strategy = self._rerun_strategy[:self._reruns + 1]

            rerun_round = request.node.execution_count - 1
            self._round_rerun_strategy = self._init_rerun_strategy[rerun_round]

            #  以下为判断log策略内容和参数的方法,注意,如果没有则设置为off
            if "screenshot" in self._round_rerun_strategy:
                self._screenshot_option = self._round_rerun_strategy.split("=")[-1]
            else:
                self._screenshot_option = "off"
            if "video" in self._round_rerun_strategy:
                self._video_option = self._round_rerun_strategy.split("=")[-1]
            else:
                self._video_option = "off"
            if "tracing" in self._round_rerun_strategy:
                self._tracing_option = self._round_rerun_strategy.split("=")[-1]
            else:
                self._tracing_option = "off"
            self._capture_trace = self._tracing_option in ["on", "retain-on-failure"]
        else:
            #  没有重试log策略和重试次数,自然取原始的log策略
            self._screenshot_option = self._pytestconfig.getoption("--screenshot")
            self._video_option = self._pytestconfig.getoption("--video")
            self._tracing_option = pytestconfig.getoption("--tracing")
            self._capture_trace = self._tracing_option in ["on", "retain-on-failure"]

    def did_finish_test(self, failed: bool) -> None:
        #  获取当前轮次并初始化一个字符串,给保存文件做前缀
        round_prefix = f"round{self._request.node.execution_count}-"
        #  这里可以学习一下组合的布尔逻辑
        capture_screenshot = self._screenshot_option == "on" or (
                failed and self._screenshot_option == "only-on-failure"
        )
        if capture_screenshot:
            for index, screenshot in enumerate(self._screenshots):
                human_readable_status = "failed" if failed else "finished"
                screenshot_path = _build_artifact_test_folder(
                    self._pytestconfig,
                    self._request,
                    #  原始为 f"test-{human_readable_status}-{index + 1}.png",
                    f"{round_prefix}{index + 1}-{human_readable_status}-{screenshot.split(os.sep)[-1]}.png",
                )
                #  这里这种写法注意下,如果自己需要放log,用这个方式创建很好
                os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
                shutil.move(screenshot, screenshot_path)
                # allure附加图片文件的方法
                allure.attach.file(screenshot_path, f"{round_prefix}{index + 1}-{human_readable_status}-{screenshot.split(os.sep)[-1]}.png")
        else:
            for screenshot in self._screenshots:
                os.remove(screenshot)

        if self._tracing_option == "on" or (
                failed and self._tracing_option == "retain-on-failure"
        ):
            for index, trace in enumerate(self._traces):
                trace_file_name = (
                    f"{round_prefix}trace.zip" if len(self._traces) == 1 else f"{round_prefix}trace-{index + 1}.zip"
                )
                trace_path = _build_artifact_test_folder(
                    self._pytestconfig, self._request, trace_file_name
                )
                os.makedirs(os.path.dirname(trace_path), exist_ok=True)
                shutil.move(trace, trace_path)
                # allure附加zip文件的方法
                allure.attach.file(trace_path, "trace.playwright.dev", extension="zip")
        else:
            for trace in self._traces:
                os.remove(trace)

        preserve_video = self._video_option == "on" or (
                failed and self._video_option == "retain-on-failure"
        )
        if preserve_video:
            for index, page in enumerate(self._all_pages):
                video = page.video
                if not video:
                    continue
                try:
                    video_file_name = (
                        f"{round_prefix}video.webm"
                        if len(self._all_pages) == 1
                        else f"{round_prefix}video-{index + 1}.webm"
                    )
                    video.save_as(
                        path=_build_artifact_test_folder(
                            self._pytestconfig, self._request, video_file_name
                        )
                    )
                    # allure附加webm录像的方法
                    allure.attach.file(_build_artifact_test_folder(
                        self._pytestconfig, self._request, video_file_name
                    ), "过程录像", allure.attachment_type.WEBM)
                except Error:
                    # Silent catch empty videos.
                    pass
        else:
            for page in self._all_pages:
                # Can be changed to "if page.video" without try/except once https://github.com/microsoft/playwright-python/pull/2410 is released and widely adopted.
                if self._video_option in ["on", "retain-on-failure"]:
                    try:
                        page.video.delete()
                    except Error:
                        pass

    def on_did_create_browser_context(self, context: BrowserContext) -> None:
        base_url = GlobalMap.get("baseurl")
        context.on("page", lambda page: self._all_pages.append(page))
        global api_count_list

        def on_page(page: Page):
            def on_clear(my_page: Page):
                try:
                    api_count_list.clear()
                    my_page.wait_for_timeout(500)
                except:
                    pass

            page.on("close", on_clear)
            page.on("load", on_clear)

        def on_add_request(req):
            if any(fix in req.url for fix in [base_url]):
                api_count_list.append(req.url)

        def on_remove_request(req):
            try:
                api_count_list.remove(req.url)
            except:
                pass

        context.on("page", on_page)
        context.on("request", on_add_request)
        context.on("requestfinished", on_remove_request)
        context.on("requestfailed", on_remove_request)

        # 判断是否需要trace，如果需要，就开始录制
        if self._request and self._capture_trace:
            context.tracing.start(
                title=slugify(self._request.node.name),
                screenshots=True,
                snapshots=True,
                sources=True,
            )

    def on_will_close_browser_context(self, context: BrowserContext) -> None:
        if self._capture_trace:
            trace_path = Path(self._pw_artifacts_folder.name) / create_guid()
            context.tracing.stop(path=trace_path)
            self._traces.append(str(trace_path))
        else:
            context.tracing.stop()

        if self._screenshot_option in ["on", "only-on-failure"]:
            for page in context.pages:
                try:
                    screenshot_path = (
                        # Path(self._pw_artifacts_folder.name) / create_guid()
                        Path(self._pw_artifacts_folder.name) / "".join([page.title(), str(time.time_ns())])
                    )
                    page.screenshot(
                        timeout=5000,
                        path=screenshot_path,
                        full_page=self._pytestconfig.getoption(
                            "--full-page-screenshot"
                        ),
                    )
                    self._screenshots.append(str(screenshot_path))
                except Error:
                    pass


def create_guid() -> str:
    return hashlib.sha256(os.urandom(16)).hexdigest()

@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session):
    if session.config.getoption("--allure_report_auto_open") == "on":
        if sys.platform != "linux":
            import subprocess
            allure_report_dir = session.config.getoption("--alluredir")
            # 尝试关闭可能已经在运行的Allure 服务
            try:
                if sys.platform == "darwin":
                    subprocess.call("pkill -f 'allure'", shell=True)
                elif sys.platform == "win32":
                    command = "taskkill /F /IM allure.exe /T"
                    subprocess.call(command, shell=True)
            except Exception as e:
                print(e)
            allure_command = f'allure serve {allure_report_dir}'
            subprocess.Popen(allure_command, shell=True)

class Locator(_Locator):
    __last_step = None

    @property
    def selector(self):
        _repr = self.__repr__()
        if "selector" in _repr:
            __selector = []
            for _ in _repr.split("selector=")[1][1:-2].split(" >> "):
                if r"\\u" not in _:
                    __selector.append(_)
                    continue
                __selector.append(
                    _.encode("utf8")
                    .decode("unicode_escape")
                    .encode("utf8")
                    .decode("unicode_escape")
                )
            return " >> ".join(__selector)

    def __getattribute__(self, attr):
        global api_Count
        global time_out
        try:
            orig_attr = super().__getattribute__(attr)
            if callable(orig_attr):

                def wrapped(*args, **kwargs):
                    step_title = None
                    if attr == "_sync" and self.__last_step:
                        step_title = self.__last_step
                    else:
                        self.__last_step = attr
                    start_time = time.time()
                    while True:
                        self.page.wait_for_load_state()
                        if time.time() - start_time < int(time_out / 1333):
                            try:
                                if attr in ["click", "fill", "hover", "check", "blur", "focus"]:
                                    self.page.wait_for_timeout(100)
                                    api_length = len(api_Count)
                                    if api_Count:
                                        self.page.wait_for_timeout(200)
                                        self.page.evaluate('''() => {
                                               const spanToRemove = document.getElementById('ainotestgogogo');
                                               if (spanToRemove) {
                                                   spanToRemove.remove();
                                               }
                                           }''')
                                        self.page.evaluate(f'''() => {{
                                                const span = document.createElement('span');
                                                span.textContent = '{attr}:{api_length}';
                                                span.style.position = 'absolute';
                                                span.style.top = '0';
                                                span.style.left = '50%';
                                                span.style.transform = 'translateX(-50%)';
                                                span.style.backgroundColor = 'yellow'; // 设置背景色以便更容易看到
                                                span.style.zIndex = '9999';
                                                span.id = 'ainotestgogogo';
                                                document.body.appendChild(span);
                                            }}''')
                                    else:
                                        # 在这里可以添加自己需要等待或者处理的动作,比如等待转圈,关闭弹窗等等(当然,弹窗最好单独做个监听)
                                        self.page.locator("//*[contains(@class, 'spin-dot-spin')]").locator("visible=true").last.wait_for(state="hidden", timeout=30_000)
                                        if self.page.locator('//div[@class="antHcbm_routesDashboardCardsHcbmCards_down"][text()="关闭"]').locator("visible=true").or_(self.page.locator(".driver-close-btn").filter(has_text="关闭").locator("visible-true")).count():
                                            self.page.locator('//div[@class="antHcbm_routesDashboardCardsHcbmCards_down"][text()="关闭"]').locator("visible=true").or_(self.page.locator(".driver-close-btn").filter(has_text="关闭").locator("visible-true")).last.evaluate("node => node.click()")
                                        self.page.evaluate('''() => {
                                                const spanToRemove = document.getElementById('ainotestgogogo');
                                                if (spanToRemove) {
                                                    spanToRemove.remove();
                                                }
                                            }''')
                                        self.page.evaluate(f'''() => {{
                                                const span = document.createElement('span');
                                                span.textContent = '{attr}:{api_length}';
                                                span.style.position = 'absolute';
                                                span.style.top = '0';
                                                span.style.left = '50%';
                                                span.style.transform = 'translateX(-50%)';
                                                span.style.backgroundColor = 'green'; // 设置背景色以便更容易看到
                                                span.style.zIndex = '9999';
                                                span.id = 'ainotestgogogo';
                                                document.body.appendChild(span);
                                            }}''')
                                        break
                                else:
                                    break
                            except:
                                self.page.evaluate('''() => {
                                        const spanToRemove = document.getElementById('ainotestgogogo');
                                        if (spanToRemove) {
                                            spanToRemove.remove();
                                        }
                                    }''')
                                self.page.evaluate(f'''() => {{
                                        const span = document.createElement('span');
                                        span.textContent = '操作等待中.....';
                                        span.style.position = 'absolute';
                                        span.style.top = '0';
                                        span.style.left = '50%';
                                        span.style.transform = 'translateX(-50%)';
                                        span.style.backgroundColor = 'red'; // 设置背景色以便更容易看到
                                        span.style.zIndex = '9999';
                                        span.id = 'ainotestgogogo';
                                        document.body.appendChild(span);
                                    }}''')
                                break
                        else:
                            self.page.evaluate('''() => {
                                    const spanToRemove = document.getElementById('ainotestgogogo');
                                    if (spanToRemove) {
                                        spanToRemove.remove();
                                    }
                                }''')
                            escaped_api_count = json.dumps(api_Count)
                            self.page.evaluate(f'''() => {{
                                    const span = document.createElement('span');
                                    span.textContent = `当前列表内容为: {escaped_api_count}`;
                                    span.style.position = 'absolute';
                                    span.style.top = '0';
                                    span.style.left = '50%';
                                    span.style.transform = 'translateX(-50%)';
                                    span.style.backgroundColor = 'red'; // 设置背景色以便更容易看到
                                    span.style.zIndex = '9999';
                                    span.id = 'ainotestgogogo';
                                    document.body.appendChild(span);
                                }}''')
                            if sys.platform != "linux":
                                print("接口卡超时了,暂时放行,需要查看超时接口或调整接口监听范围:")
                                print(escaped_api_count)
                                pass
                            api_Count.clear()
                            break

                    if step_title:
                        with step(f"{step_title}: {self.selector}"):
                            return orig_attr(*args, **kwargs)
                    return orig_attr(*args, **kwargs)

                return wrapped
            return orig_attr
        except AttributeError:
            ...


mapping.register(LocatorImpl, Locator)