import os
import time
import logging
from typing import List, Dict

import aiohttp
import asyncio
from colorama import Style

cyan = "\033[38;5;159m"
pink = "\033[38;5;218m"
green = "\033[1;32m"
yellow = "\033[1;33m"
red = "\033[1;31m"
white = "\033[1;37m"
r = Style.RESET_ALL

logging.basicConfig(level=logging.INFO, format=f"{white}[{r}%(asctime)s{white}]{r} - {cyan}%(levelname)s{r} - {pink}%(message)s{r}", datefmt=f"{pink}%H{r}{cyan}:{r}{pink}%M{r}{cyan}:{r}{pink}%S{r}", handlers=[logging.FileHandler("checker.log"), logging.StreamHandler()])

logo = f"""{pink}

 ░▒▓███████▓▒░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
 ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░   
       ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
       ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓███████▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓████████▓▒░{r}
"""

class TokenChecker:
    def __init__(self, tokens: str = "input/tokens.txt"):
        self.tokenn = tokens
        self.valid: List[str] = []
        self.locked: List[str] = []
        self.invalid: List[str] = []
        self.delay = 0.5
        os.system("cls")
        os.system("title Token Checker")
        print(logo)

    def validate_tokens(self, tokens: List[str]) -> List[str]:
        starts = ('MT', 'Nz', 'OT', 'OD', 'Nj', 'NT')
        realtokens = []
        for token in tokens:
            token = token.replace('"', '').replace("'", '').strip()
            if token.startswith(starts):
                realtokens.append(token)
        return realtokens

    async def get(self) -> List[str]:
        try:
            with open(self.tokenn, "r") as file:
                tokens = [line.strip() for line in file if line.strip()]
            
            tokens = self.validate_tokens(tokens)
            tokens = list(set(tokens))
            
            logging.info(f"Loaded {len(tokens)} valid tokens from {self.tokenn}")
            print()
            return tokens
        except FileNotFoundError:
            logging.error(f"{self.tokenn} not found")
            return []

    async def check_token(self, session: aiohttp.ClientSession, token: str) -> None:
        url = "https://discord.com/api/v10/users/@me/library"
        headers = {
            'authority': 'discord.com',
            'accept': '*/*',
            'authorization': token,
            'accept-language': 'sv,sv-SE;q=0.9',
            'content-type': 'application/json',
            'origin': 'https://discord.com',
            'referer': 'https://discord.com/',
            'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9016 Chrome/108.0.5359.215 Electron/22.3.12 Safari/537.36',
            'x-debug-options': 'bugReporterEnabled',
            'x-discord-locale': 'sv-SE',
            'x-discord-timezone': 'Europe/Stockholm',
            'x-super-properties': 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDE2Iiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDUiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6InN2IiwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV09XNjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIGRpc2NvcmQvMS4wLjkwMTYgQ2hyb21lLzEwOC4wLjUzNTkuMjE1IEVsZWN0cm9uLzIyLjMuMTIgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjIyLjMuMTIiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjoyMTg2MDQsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjM1MjM2LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==',
        }

        try:
            async with session.get(url, headers=headers) as response:
                status = response.status
                if status == 200:
                    self.valid.append(token)
                    logging.info(f"{green}Valid{r} {pink}{token[:25]}{r}...")
                elif status == 403:
                    self.locked.append(token)
                    logging.info(f"{yellow}Locked{r} {pink}{token[:25]}{r}...")
                elif status == 429:
                    ret = int(response.headers.get("Retry-After", 1))
                    logging.info(f"{red}Rate limited, Retrying after {ret} seconds.{r}")
                    await asyncio.sleep(ret)
                    return await self.check_token(session, token)
                else:
                    self.invalid.append(token)
                    logging.info(f"{red}Invalid{r} {pink}{token[:25]}{r}...")
        except Exception as _:
            logging.error(_)
            self.invalid.append(token)

        time.sleep(self.delay)

    async def check(self) -> Dict[str, List[str]]:
        tokens = await self.get()
        if not tokens:
            return {"valid": [], "locked": [], "invalid": []}

        async with aiohttp.ClientSession() as session:
            tasks = [self.check_token(session, token) for token in tokens]
            await asyncio.gather(*tasks)

        return {
            "valid": self.valid,
            "locked": self.locked,
            "invalid": self.invalid,
        }

    async def save(self) -> None:
        print()
        os.makedirs("output", exist_ok=True)
        with open("output/valid.txt", "w") as valid_file:
            valid_file.write("\n".join(self.valid))
        logging.info(f"{green}Saved valid tokens to output/valid.txt{r}")

        with open("output/locked.txt", "w") as locked_file:
            locked_file.write("\n".join(self.locked))
        logging.info(f"{yellow}Saved locked tokens to output/locked.txt{r}")

        with open("output/invalid.txt", "w") as invalid_file:
            invalid_file.write("\n".join(self.invalid))
        logging.info(f"{red}Saved invalid tokens to output/invalid.txt{r}")

    async def run(self) -> None:
        while True:
            try:
                self.delay = float(input(f"{pink}Delay:{r} "))
                print()
                if self.delay <= 0:
                    logging.error(f"{red}Failed{r}")
                    continue
                break
            except ValueError:
                logging.error(f"{red}put a delay{r}")

        results = await self.check()
        print()
        logging.info(f"{green}Valid:   {len(results['valid'])}")
        logging.info(f"{yellow}Locked:  {len(results['locked'])}")
        logging.info(f"{red}Invalid: {len(results['invalid'])}")

        await self.save()

        input("\nPress enter to exit ")
        exit(0)


if __name__ == "__main__":
    checker = TokenChecker()
    asyncio.run(checker.run())
