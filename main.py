import odapi_client
import TM1638

DIO = 17
CLK = 21
STB = 22
config = odapi_client.OdApiConfg.load("config.json")

client = odapi_client.OdApiClient(config)
# words = client.get_word_list({"registers": "Coarse_Slang"})
words = client.get_word_list({"lexicalCategory": "noun,adjective"})
print words

display = TM1638.TM1638(DIO, CLK, STB, sleep_time=0.0005)
display.enable(intensity=3)

for word in words:
    try:
        definition = client.define_word(word)
        print definition
        display.scroll_text("")
        display.scroll_text(u"- {} - {}".format(word, definition))
    except odapi_client.ODAPIClientException as e:
        pass