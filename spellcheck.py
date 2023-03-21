import requests

def check(text):
    api_key = "c4479fb57ebf4c9c9e872cf972e943f8"
    endpoint = "https://api.bing.microsoft.com/v7.0/spellcheck"
    data = {'text': text}
    params = {'mkt':'en-us', 'mode':'spell'}
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    response = requests.post(endpoint, headers=headers, params=params, data=data)
    json_response = response.json()
    if json_response["flaggedTokens"]:
        correction = json_response["flaggedTokens"][0]["suggestions"][0]["suggestion"]
        return correction[0].upper() + correction[1:]
    else:
        return text

def correctSpell(text):
    api_key = "c4479fb57ebf4c9c9e872cf972e943f8"
    endpoint = "https://api.bing.microsoft.com/v7.0/spellcheck"
    data = {'text': text}
    params = {'mkt':'en-us', 'mode':'spell'}
    headers = {'Ocp-Apim-Subscription-Key': api_key}
    response = requests.post(endpoint, headers=headers, params=params, data=data)
    json_response = response.json()
    flaggedTokens = json_response["flaggedTokens"]
    if flaggedTokens:
        new_words = {}
        for flaggedToken in flaggedTokens:
            word = flaggedToken["token"]
            new_word = flaggedToken["suggestions"][0]["suggestion"]
            if word[0].isupper():
                new_word = new_word.capitalize()
            if word[-2:] == "'s" and new_word[-2:] != "'s":
                new_word = new_word[:-1] + "'s"
            offset = flaggedToken["offset"]
            new_words[offset] = [word, new_word]
        words = ""
        i = 0
        while i < len(text):
            if i in new_words:
                words += new_words[i][1]
                i += len(new_words[i][0])
            else:
                words += text[i]
                i += 1
        return words
    return text

if __name__ == '__main__':
    example_text = "What is Dr.Clemant's email"
    print(check("Peterrrsan"))
