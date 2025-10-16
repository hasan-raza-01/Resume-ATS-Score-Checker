from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import asyncio
import aiofiles
import time
from pathlib import Path
from .base import *
from ...exception import CustomException
import sys

class HTMLParser(BaseParser):
    
    def can_handle(self, file_type: str) -> bool:
        return file_type == "html"
    
    async def parse(self, path: Path) -> str:
        """Parse HTML with static-first, rendering fallback strategy"""
        try:
            needs_rendering = await self._detect_dynamic_html(path)
            
            if not needs_rendering:
                return await self._extract_static_html(path)
            else:
                return await self._extract_rendered_html(path)
                
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    async def _detect_dynamic_html(self, file_path: Path) -> bool:
        """Check if HTML needs dynamic rendering"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
            
            loop = asyncio.get_event_loop()
            
            def _analyze_content():
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove scripts/styles for content check
                for script in soup(["script", "style"]):
                    script.decompose()
                
                visible_text = soup.get_text().strip()
                
                # If very little static content, likely needs rendering
                if len(visible_text) < 100:
                    return True
                
                # Check for SPA indicators
                spa_indicators = ['ng-app', 'data-reactroot', 'v-app', 'id="app"', 'id="root"']
                html_lower = html_content.lower()
                return any(indicator in html_lower for indicator in spa_indicators)
            
            return await loop.run_in_executor(None, _analyze_content)
            
        except Exception as e:
            e = CustomException(e, sys)
            self.logger.error(e)
            return False
    
    async def _extract_static_html(self, file_path: Path) -> str:
        """Extract using BeautifulSoup (native method)"""
        try:
            loop = asyncio.get_event_loop()
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                html_content = await f.read()
            
            def _parse_static():
                soup = BeautifulSoup(html_content, 'html.parser')
                full_text = ""
                
                # Remove scripts/styles
                for tag in soup(["script", "style"]):
                    tag.decompose()
                
                # Extract headings, paragraphs, lists
                for element in soup.find_all(['h1','h2','h3','h4','h5','h6','p','li']):
                    text = element.get_text().strip()
                    if text:
                        full_text += text + "\n"
                
                # Extract tables
                for i, table in enumerate(soup.find_all("table")):
                    full_text += f"\nTable {i}\n"
                    for row in table.find_all("tr"):
                        cells = [c.get_text(strip=True) for c in row.find_all(['td','th'])]
                        if cells:
                            full_text += " | ".join(cells) + "\n"
                
                return full_text
            
            result = await loop.run_in_executor(None, _parse_static)
            self.logger.info("parsed through native method")
            return result
        except Exception as e:
            e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    async def _extract_rendered_html(self, file_path: Path, timeout: int = 20) -> str:
        """Smart rendering with multiple wait strategies"""
        try:
            loop = asyncio.get_event_loop()
            
            def _render_html():
                driver = None
                try:
                    driver = self._setup_driver()
                    driver.get(f"file://{file_path.absolute()}")
                    
                    # Multi-strategy waiting
                    rendered_html = self._wait_for_page_load(driver, timeout)
                    return self._parse_rendered_content(rendered_html)
                    
                finally:
                    if driver:
                        driver.quit()
            
            result = await loop.run_in_executor(None, _render_html)
            self.logger.info("parsed through rendering")
            return result
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    def _wait_for_page_load(self, driver, timeout):
        """Comprehensive waiting strategy"""
        try:
            wait = WebDriverWait(driver, timeout)
            
            # 1. Wait for DOM ready
            wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
            
            # 2. Wait for minimum content
            try:
                wait.until(lambda d: len(d.find_element(By.TAG_NAME, "body").text) > 100)
            except TimeoutException:
                pass
            
            # 3. Content stability check
            self._wait_for_stability(driver, max_checks=5)
            
            return driver.page_source
        except Exception as e:
            if not isinstance(e, CustomException):
                e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    def _wait_for_stability(self, driver, max_checks=5):
        """Wait until page content stops changing"""
        try:
            previous_content = ""
            stable_count = 0
            
            for _ in range(max_checks):
                time.sleep(1)
                try:
                    current_content = driver.find_element(By.TAG_NAME, "body").text
                    if current_content == previous_content and len(current_content) > 50:
                        stable_count += 1
                        if stable_count >= 2:  # Stable for 2 seconds
                            break
                    else:
                        stable_count = 0
                    previous_content = current_content
                except:
                    break
        except Exception as e:
            e = CustomException(e, sys)
            self.logger.error(e)
            raise e
    
    def _parse_rendered_content(self, rendered_html: str) -> str:
        """Parse the rendered HTML content"""
        try:
            full_text = ""
            soup = BeautifulSoup(rendered_html, 'html.parser')
            
            # Remove scripts/styles
            for tag in soup(["script", "style"]):
                tag.decompose()
            
            # Extract headings, paragraphs, lists
            for element in soup.find_all(['h1','h2','h3','h4','h5','h6','p','li']):
                text = element.get_text().strip()
                if text:
                    full_text += text + "\n"
            
            # Extract tables
            for i, table in enumerate(soup.find_all("table")):
                full_text += f"\nTable {i}\n"
                for row in table.find_all("tr"):
                    cells = [c.get_text(strip=True) for c in row.find_all(['td','th'])]
                    if cells:
                        full_text += " | ".join(cells) + "\n"
            return full_text
        
        except Exception as e:
            e = CustomException(e, sys)
            self.logger.error(e)
            raise e

__all__ = ["HTMLParser"]
