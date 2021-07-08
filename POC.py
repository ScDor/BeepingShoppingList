import pandas as pd
import xmltodict
from zxing import BarCodeReader

INVALID_BARCODE = -1

barcode_reader = BarCodeReader()


def parse_hazi_hinam(filename: str = 'hazi_hinam_dummy.xml') -> pd.DataFrame:
    """ parses a price file from Hazi-Hinam's data"""
    prices_xml = open(filename, encoding='utf8').read
    prices_dict = xmltodict.parse(prices_xml())
    return pd.DataFrame(prices_dict['Root']['Items']['Item'])


def get_product_name(df: pd.DataFrame, item_code: int) -> str:
    """
    :param df: Price data table, with ItemCode and ItemName columns
    :param item_code: Barcode of the item
    :return: Name of the item
    """
    if item_code == INVALID_BARCODE:
        return "Invalid barcode"

    try:
        return df[df['ItemCode'] == str(item_code)].iloc[0]['ItemName']
    except IndexError:
        return "N/A"


def decode_first_barcode(filename: str) -> int:
    """
    :param filename: Path to an image file
    :return: First barcode decoded by pyzbar in the image
    """
    decoded = barcode_reader.decode(filename)
    try:
        return int(decoded.parsed)
    except TypeError:
        return INVALID_BARCODE


if __name__ == '__main__':
    """ Proof of concept - returns name of the product whose barcode appears in an image """
    prices = parse_hazi_hinam()
    barcode = decode_first_barcode('milk.jpg')
    print(get_product_name(prices, barcode))
