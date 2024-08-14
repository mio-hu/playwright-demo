import pytest
import allure
import os
from conf.config import base_config
from playwright.sync_api import Page, expect, BrowserContext
from pages import PageInstance
