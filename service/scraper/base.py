import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

logger = logging.getLogger(__name__)


@dataclass
class ScrapedProduct:
    """Intermediate data container for a scraped product before DB persistence."""
    external_id: str
    name: str
    link: str
    price: Decimal
    currency: str = "USD"
    description: Optional[str] = None
    seller_name: Optional[str] = None
    rating: Optional[Decimal] = None
    rating_count: Optional[int] = None
    discount: Optional[Decimal] = None
    image_urls: list[str] = field(default_factory=list)


@dataclass
class ScrapedGeneralResult:
    """Lightweight result returned from a search listing page."""
    external_id: str
    image_url: str
    name: str
    link: str
    price: Optional[Decimal] = None
    discount: Optional[float] = None
    currency: str = "USD"


class BaseShopScraper(ABC):
    """
    Abstract base class for online shop scrapers powered by Selenium.
    """

    base_url: str  # Must be defined by each subclass

    def __init__(
        self,
        headless: bool = True,
        implicit_wait: int = 5,
        page_load_timeout: int = 30,
        driver_path: Optional[str] = None,
    ):
        self.headless = headless
        self.implicit_wait = implicit_wait
        self.page_load_timeout = page_load_timeout
        self.driver_path = driver_path
        self._driver: Optional[WebDriver] = None

    # ------------------------------------------------------------------
    # Driver lifecycle
    # ------------------------------------------------------------------

    def _build_options(self) -> Options:
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--disable-blink-features=AutomationControlled")
        return options

    def _create_driver(self) -> WebDriver:
        options = self._build_options()
        service = Service(self.driver_path) if self.driver_path else Service()
        driver = webdriver.Firefox(service=service, options=options)
        driver.implicitly_wait(self.implicit_wait)
        driver.set_page_load_timeout(self.page_load_timeout)
        return driver

    @property
    def driver(self) -> WebDriver:
        if self._driver is None:
            raise RuntimeError("Driver is not started. Use the context manager or call start().")
        return self._driver

    def start(self) -> "BaseShopScraper":
        """Initialise the WebDriver and navigate to base_url."""
        logger.info("Starting WebDriver for %s", self.__class__.__name__)
        self._driver = self._create_driver()
        self._driver.get(self.base_url)
        self._accept_cookies()
        return self

    def quit(self) -> None:
        """Cleanly close the WebDriver session."""
        if self._driver:
            logger.info("Quitting WebDriver for %s", self.__class__.__name__)
            self._driver.quit()
            self._driver = None

    def __enter__(self) -> "BaseShopScraper":
        return self.start()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.quit()

    # ------------------------------------------------------------------
    # Helpers available to all subclasses
    # ------------------------------------------------------------------

    def wait_for(self, locator: tuple, timeout: int = 10) -> None:
        """Block until the element identified by *locator* is visible."""
        return WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def safe_find_text(self, by: str, value: str, default: str = "") -> str:
        """Return the text of the first matching element, or *default* on failure."""
        try:
            return self.driver.find_element(by, value).text.strip()
        except Exception:
            return default

    def navigate(self, url: str) -> None:
        """Navigate to an arbitrary URL and wait for the page to load."""
        logger.debug("Navigating to %s", url)
        self.driver.get(url)

    # ------------------------------------------------------------------
    # Optional hooks
    # ------------------------------------------------------------------

    def _accept_cookies(self) -> None:
        """
        Override to dismiss cookie consent banners.
        Called automatically after the initial page load.
        """
    
    def _find_element_nowait(self, by: str, selector: str, parent = None):
        self.driver.implicitly_wait(0)
        element = (parent or self.driver).find_elements(by, selector)
        self.driver.implicitly_wait(self.implicit_wait)
        if len(element) > 0:
            return element[0]
       

    def _is_logged_in(self) -> bool:
        """Override to check whether the current session is authenticated."""
        return False

    def login(self, username: str, password: str) -> None:
        """
        Override to implement shop-specific login flow.
        Raise NotImplementedError if the shop does not support authentication.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement login().")

    # ------------------------------------------------------------------
    # Abstract interface — must be implemented by every subclass
    # ------------------------------------------------------------------
    @abstractmethod
    def get_homepage_products(self, max_results: int = 20) -> list[ScrapedGeneralResult]:
        ...

    @abstractmethod
    def search(self, query: str, max_results: int = 20) -> list[ScrapedGeneralResult]:
        """
        Search the shop for *query* and return up to *max_results* listings.

        Args:
            query:       The search keyword(s).
            max_results: Maximum number of results to return.

        Returns:
            A list of ScrapedSearchResult instances.
        """

    @abstractmethod
    def get_product(self, external_id: str) -> ScrapedProduct:
        """
        Scrape full product details for the given *external_id*.

        Args:
            external_id: The shop-specific product identifier
                         (e.g. ASIN for Amazon, item number for eBay).

        Returns:
            A fully populated ScrapedProduct instance.
        """