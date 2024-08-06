from playwright.sync_api import Page, expect, BrowserContext
from pages.base_page import instance_all_pages
from utils.global_map import GlobalMap
from conf.config import base_config
from utils.path import get_path
import allure
import pytest
