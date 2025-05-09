from FileAndDirectoryController import FileDirectoryController
from JSONController import JSONController
from RequestController import RequestController

class YgoproController:
    def __init__(self, max_threads):
        FileDirectoryController().create_directory("Data/Ygodata/Images")
        FileDirectoryController().write_file("Data/Ygodata", "YgoproData.json")
        if FileDirectoryController().is_file_empty("Data/Ygodata", "YgoproData.json"):
            JSONController().dump_webpage_to_json("Data/Ygodata", "YgoproData.json", 'https://db.ygoprodeck.com/api/v7/cardinfo.php', external_key='data')
        self.ygopro_data = JSONController().load_json("Data/Ygodata", "YgoproData.json")
        self.max_threads = max_threads

    def download_all_images_thread(self, thread_id):
        for i in range(thread_id, len(self.ygopro_data), self.max_threads):
            card = list(self.ygopro_data)[i]
            if not FileDirectoryController().does_path_exist(f"Data/Ygodata/Images/{card['id']}.jpg"):
                RequestController().download_image(card['card_images'][0]['image_url'], f"Data/Ygodata/Images/{card['id']}.jpg")
            print(f"{i}/{len(self.ygopro_data)}")

    def FindCardByID(self, id):
        scrubbedid = self.ScrubID(int(id))
        for card in self.ygopro_data:
            if card['id'] == scrubbedid:
                return card
        return None

    def FindCardIDNullCheck(self, id):
        find_card = self.FindCardByID(id)
        if find_card is None:
            print(f"Card Is Null: {id}")
        return find_card

    def FindCardByName(self, name):
        for card in self.ygopro_data:
            if card['name'] == name:
                return card
        return None

    def ScrubID(self, theirid):
        if theirid == 83011277:
            return 83011278
        if theirid == 83555667:
            return 7852509
        if theirid == 84080938:
            return 84080939
        if theirid == 18807108:
            return 18807109
        if theirid == 36996508:
            return 38033121
        if theirid == 73134081:
            return 73134082
        if theirid == 19230407:
            return 19230408
        if theirid == 16195943:
            return 16195942
        if theirid == 83764718:
            return 83764719
        if theirid == 6150045:
            return 6150044
        if theirid == 57116034:
            return 57116033
        if theirid == 39751093:
            return 39751094
        if theirid == 81480460:
            return 81480461
        if theirid == 77585514:
            return 77585513
        if theirid == 27847700:
            return 24094653
        if theirid == 44508095:
            return 44508094
        return theirid