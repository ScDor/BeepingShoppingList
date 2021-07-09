import os

import pandas as pd
import xmltodict
from zxing import BarCodeReader

COMMAND_EXIT = -1
COMMAND_EMPTY_LIST = 0

barcode_reader = BarCodeReader()


class ShoppingList:
    def __init__(self):
        self.products = {}

    def __str__(self):
        return "\n".join(
            (f"{amount}\t{name}" for (name, amount) in self.products.items())
        )

    def add_product(self, item: str):
        if item in self.products:
            self.products[item] += 1
        else:
            self.products[item] = 1

    def empty(self):
        self.products = {}


class ProductException(BaseException):
    pass


def parse_hazi_hinam(filename: str = 'hazi_hinam_dummy.xml') -> pd.DataFrame:
    """ parses a price file from Hazi-Hinam's data"""
    prices_xml = open(filename, encoding='utf8').read
    prices_dict = xmltodict.parse(prices_xml())
    return pd.DataFrame(prices_dict['Root']['Items']['Item'])


def decode_first_barcode(filename: str) -> int:
    """
    :param filename: Path to an image file
    :return: First barcode decoded in the image
    """
    decoded = barcode_reader.decode(filename)
    try:
        return int(decoded.parsed)
    except TypeError:
        raise ProductException(f"Invalid barcode: {decoded.parsed}")
    except AttributeError:
        raise ProductException(f"Cannot find barcode")


def get_product_name(df: pd.DataFrame, item_code: int) -> str:
    """
    :param df: Price data table, with ItemCode and ItemName columns
    :param item_code: Barcode of the item
    :return: Name of the item
    """
    try:
        return df[df['ItemCode'] == str(item_code)].iloc[0]['ItemName']
    except IndexError:
        raise ProductException(f"Item {item_code} was not found in database")


def demo_input() -> None:
    prices = parse_hazi_hinam()
    shopping_list = ShoppingList()
    barcode_raw = ""  # demo only

    print("DEMO: here are some barcodes to test with: "
          "7290004127336, 7290000144474, 7290000311203, 7290004131074"
          "\n")

    print("Type  0 to empty the list")
    print("Type -1 to exit")

    # in real life, will output to some endpoint rather than print
    while True:
        try:
            barcode_raw = input("Scan an item to continue\t")
            barcode = int(barcode_raw)

            if barcode == COMMAND_EMPTY_LIST:
                print("Shopping list emptied successfully")
                shopping_list.empty()
                continue

            elif barcode == COMMAND_EXIT:
                print("Here's your shopping list, goodbye!")
                print("-" * 40)
                print(shopping_list)
                print("-" * 40)
                exit(0)

            else:
                product = get_product_name(prices, barcode)
                shopping_list.add_product(product)

                print('Beep!')
                print(shopping_list)
                print()

        except TypeError:
            # for demo purposes only
            # in real-life this happens in decode_first_barcode()
            print(f"Not an integer:{barcode_raw}")

        except ValueError:
            # for demo purposes only
            print(f"Not an integer:{barcode_raw}")

        except ProductException as e:
            print(e)


def demo_images() -> None:
    prices = parse_hazi_hinam()
    shopping_list = ShoppingList()

    for picture in os.listdir('demo_pictures'):
        print(f"Scanning item in {picture} --- ", end="")
        picture_path = os.path.join('demo_pictures', picture)

        try:
            barcode = decode_first_barcode(picture_path)
            product = get_product_name(prices, barcode)
            shopping_list.add_product(product)

        except ProductException as e:
            print(f'{picture_path}: {e}')
            print()

        print('Beep!')
        print(shopping_list)
        print()


if __name__ == '__main__':
    """ 
    run `demo_images()` for a quick hardcoded image demo 
    run `demo_input()` for interactive input 
    """
    demo_images()
