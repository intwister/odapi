import odapi_client
import TM1638
import time

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

show_definitions = True

for word in words:
    try:
        display.set_text("")

        if show_definitions:
            definition = client.define_word(word)
            print definition
            display.scroll_text(u"- {} - {}".format(word, definition), print_forward=True)
        else:
            display.scroll_text(word, print_forward=True)

        time.sleep(2)

    except odapi_client.ODAPIClientException as e:
        pass