# Plurality autotrans
Automated daily translation of the Plurality book manuscripts

## Purpose

The primary objective of this tool is to support teams translating the book into Japanese by facilitating the easy sharing of machine translation results. This promotes efficient collaboration.

While designed with Japanese translation team in mind, this system can also help teams all over the world translating into their own languages. 

This vision aligns seamlessly with Plurality's ethos:

>Plurality, as we call it, is technology that recognizes, honors, and empowers cooperation across social and cultural differences.

This tool is a technology that empowers cooperation across the difference of language.


## Features

### Automated Pull and Merge from Upstream
Using GitHub Actions, this tool automatically pulls changes from the upstream `pluralitybook/plurality` and merge them daily into our Japanese fork `nishio/plurality-japanese`.

### Automated Translation
In the Github action, it runs the translation script and commits the result.

Upsteam updates are markdown and a line in file represents a paragraph. So I designed to translate per line and cache the result. It translate only updated paragraph.

## Usage
You need OPENAI_API_KEY to use this tool, put it in `.env` file to run in local, or Github Secret to run in Github Action.

## License
Created by NISHIO Hirokazu, I license this tool under the MIT license.

## Contact

If you have any questions, feel free to ask me(NISHIO Hirokazu) on [The Plurality Book Discord](https://discord.gg/9HzwhKt6).

If you want to use Japanese, 日本語で話したい人は[Plurality翻訳 Scrapbox](https://scrapbox.io/projects/plurality-japanese/invitations/d784b3b1a8abb3902ef6731eb034e9e9)へ。