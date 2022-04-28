import re

import fake_useragent
import requests
from bs4 import BeautifulSoup

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout

from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput


class ParserApp(App):
    def __init__(self):
        super().__init__()
        self.__proxies = dict(http='socks5://127.0.0.1:9150', https='socks5://127.0.0.1:9150')
        self.__header = {'User-Agent': str(fake_useragent.UserAgent().random)}

    def build(self):
        self.title = "Scraping"
        superBox = BoxLayout(orientation="horizontal", padding=5)

        inputDataBox = BoxLayout(orientation="vertical")

        button_terminal_run = Button(text="Run in the terminal", size_hint=[1, .07], on_press=self._run_parser)

        inputDataBox.add_widget(button_terminal_run)

        self.url = TextInput(
            text="https://",
            multiline=False,
            font_size=17, size_hint=[1, .07],
            background_color=[1, 1, 1, .7])
        inputDataBox.add_widget(self.url)

        grid_dataLeft = GridLayout(size_hint=[1, .07], cols=3)

        self.file_name = TextInput(
            text="result.txt",
            multiline=False,
            font_size=17
        )
        grid_dataLeft.add_widget(self.file_name)

        button_save = Button(text="Save in the file", on_press=self._save_result)
        regular_run = Button(text="Run regular expression", on_press=self._run_regular_exp)

        grid_dataLeft.add_widget(button_save)
        grid_dataLeft.add_widget(regular_run)

        inputDataBox.add_widget(grid_dataLeft)

        self.result = TextInput(readonly=True)
        inputDataBox.add_widget(self.result)

        switchInfoBox = BoxLayout(orientation="vertical", size_hint=[.5, 0.985])

        UALabel = Label(text=": : User-agent : :", font_size=16)
        TorProxiesLabel = Label(text=": : Tor-proxies : :", font_size=16)

        self.UASwitch = Switch(size_hint=[1, .33], active=False)
        self.TorProxiesSwitch = Switch(size_hint=[1, .33], active=False)

        switchInfoRight = GridLayout(size_hint=[1, .22], cols=2)

        switchInfoRight.add_widget(UALabel)
        switchInfoRight.add_widget(self.UASwitch)

        switchInfoRight.add_widget(TorProxiesLabel)
        switchInfoRight.add_widget(self.TorProxiesSwitch)

        paramsRight = GridLayout(size_hint=[1, .09], cols=3)

        self.tag = TextInput(text="", multiline=False, hint_text="Tag", font_size=17)
        self.attribute = TextInput(text="", multiline=False, hint_text="Attribute", font_size=17)
        self.regular_exp = TextInput(text="", multiline=False, hint_text="Regular", font_size=17)

        paramsRight.add_widget(self.tag)
        paramsRight.add_widget(self.attribute)
        paramsRight.add_widget(self.regular_exp)

        switchInfoBox.add_widget(switchInfoRight)
        switchInfoBox.add_widget(paramsRight)

        self.info = TextInput(readonly=True, background_color=[1, 1, 1, .7])
        switchInfoBox.add_widget(self.info)

        switchInfoBox.add_widget(Button(text="Clear", size_hint=[1, .055], on_press=self._clear))

        superBox.add_widget(inputDataBox)
        superBox.add_widget(switchInfoBox)
        return superBox

    def __connection(self):
        __ip_site = 'https://icanhazip.com'
        try:
            if self.UASwitch.active and self.TorProxiesSwitch.active:
                self.info.text += self.__header['User-Agent']
                __address = requests.get(__ip_site, headers=self.__header, proxies=self.__proxies)
                self.info.text += f"\n:: IP Tor network: {__address.text}"
                return 'all', True
            elif self.UASwitch.active and not self.TorProxiesSwitch.active:
                self.info.text += self.__header['User-Agent']
                __address = requests.get(__ip_site, headers=self.__header)
                self.info.text += f"\n:: IP network: {__address.text}"
                return 'ua', True
            elif not self.UASwitch.active and self.TorProxiesSwitch.active:
                __address = requests.get(__ip_site, proxies=self.__proxies)
                self.info.text += f"\n:: IP Tor network: {__address.text}"
                return 'tor', True
            else:
                __address = requests.get(__ip_site)
                self.info.text += f"\n:: IP network: {__address.text}"
                return 'nothing', True
        except requests.exceptions.ConnectionError:
            self.info.text += ":: Stopping connect to the Tor network -> Check ur Tor\n"
            return 'nothing', False
        except Exception as e:
            self.info.text += ":: Stopping connect to the Tor network\n" \
                              f"\nConnection Exception: {e}\n"
            return 'nothing', False

    # todo verify=False ?
    def __get_page(self):
        turn_on, connection = self.__connection()
        url = self.url.text
        if connection:
            if turn_on == 'all':
                page = requests.get(url, proxies=self.__proxies, headers=self.__header)
            elif turn_on == 'ua':
                page = requests.get(url, headers=self.__header)
            elif turn_on == 'tor':
                page = requests.get(url, proxies=self.__proxies)
            elif turn_on == 'nothing':
                page = requests.get(url)
            else:
                raise Exception(f"Incorrect URL {url}")
            self.soup = BeautifulSoup(page.text, "html.parser")
            return True
        else:
            self.info.text += ":: Connection False.\n"

    def _run_parser(self, args):
        if self.__get_page():
            if self.tag.text:
                for tag in self.soup.findAll(self.tag.text):
                    if self.attribute.text:
                        if self.attribute.text == "inside":
                            self.result.text += f"{tag.text}\n"
                        else:
                            try:
                                self.result.text += f"{tag[self.attribute.text]}\n"
                            except KeyError:
                                pass
                    else:
                        self.result.text += f"{str(tag)}\n"
            else:
                for tag in self.soup.findAll('html'):
                    self.result.text += f"{str(tag)}\n"
            self.info.text += ":: Parse successfully runned."
        # todo
        else:
            self.info.text += ":: Parse stopped."

        # todo
        # if self.result.text:
        #     self.result.text = "Check ur params.\n"

    def _clear(self, args):
        self.result.text = ""
        self.info.text = ""

    def _run_regular_exp(self, args):
        if self.regular_exp.text:
            if self.result.text:
                regular_result = re.findall(fr'{self.regular_exp.text}', self.result.text)
                if regular_result:
                    self.result.text += f"\n\nRegular expression result:\n{regular_result}\n"
                else:
                    self.regular_exp.text = f"\nRegular expression is failed -> 0 Result.\n"
            else:
                self.regular_exp.text = f"First run parse.\n"
        else:
            self.regular_exp.text = f"Add regular expression.\n"

    def _save_result(self, args):
        try:
            with open(self.file_name.text, "w", encoding="utf-8") as file:
                file.write(self.result.text)
            self.info.text += f":: File {self.file_name.text} successfully saved."
        except Exception as e:
            self.info.text += f"Exception: {e}"


if __name__ == '__main__':
    ParserApp().run()
