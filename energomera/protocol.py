# coding=utf8

import struct
from energomera.crc8 import calc_crc
from energomera.utils import pretty_hex


ADDRESS_FMT = '!I'  # unsigned integer in network order

END = '\xC0'
ESC = '\xDB'
END_REPLACE = '%s\xDC' % ESC
ESC_REPLACE = '%s\xDD' % ESC
OPT = '\x48'
SOURCE_ADDR = '\xFD' #253
USER_PASSWORD = '\x00\x00\x00\x00' # 4 байта

GET_ENERGY = b'\x01\x30'
GET_ENERGY_SUM = b'\x00\x00' # 0 текущие значения 0 сумма по тарифам
GET_ENERGY_TARIF1 = b'\x00\x01'
GET_ENERGY_TARIF2 = b'\x00\x02'
GET_ENERGY_TARIF3 = b'\x00\x03'
GET_ENERGY_TARIF4 = b'\x00\x04'
GET_ENERGY_TARIF5 = b'\x00\x05'

ADDRESS = 65535 # широковещательный b'\xFFFF'
PING = b'\x00\x01'
VERS = b'\x01\x00'

def get_serv(direct=1, class_access=5, message_len=0): # возвращает 1 байт
    r'''
    Формирует байт для поля serv при запросе
    direct: 1-запрос, 0-ответ
    class_access: 5-выполнение 7-ошибка
    message_len: максимум 15 (4 бита)
    '''
    if message_len > 15:
        raise Exception(u'Длина сообщения не может быть больше 15 байт')

    if class_access > 7:
        raise Exception(u'Длина class_access не может быть больше 7')

    message_len = bin(message_len).lstrip('0b').zfill(4)
    class_access = bin(class_access).lstrip('0b').zfill(3)
    direct = bin(direct).lstrip('0b')
    return str(hex(int('0b'+direct+class_access+message_len, base=2))).lstrip('0x').decode("hex")

def get_pal(cmd, data, password): # data = byte_array, password=str 4 байта, cmd = 2 байта
    message_len = len(data)
    serv = get_serv(message_len=message_len)
    # cmd = cmd[1]+cmd[0]
    return password+serv+cmd+data

def get_energy(data, address=ADDRESS):
    pal = get_pal(GET_ENERGY, data, USER_PASSWORD)
    addressD = bin(address).lstrip('0b').zfill(16)
    addressDL = str(hex(int('0b'+addressD[8:], base=2))).lstrip('0x').decode("hex") or b'\x00'
    addressDH = str(hex(int('0b'+addressD[:8], base=2))).lstrip('0x').decode("hex") or b'\x00'
    addressS = bin(253).lstrip('0b').zfill(16)
    addressSL = str(hex(int('0b'+addressS[8:], base=2))).lstrip('0x').decode("hex") or b'\x00'
    addressSH = str(hex(int('0b'+addressS[:8], base=2))).lstrip('0x').decode("hex") or b'\x00'
    message = OPT+addressDL+addressDH+addressSL+addressSH+pal
    crc8 = calc_crc(message)
    return END+message+crc8+END

def get_ping(address=ADDRESS):
    pal = get_pal(PING, b'', USER_PASSWORD)
    # print 'pal:', pretty_hex(pal)
    addressD = bin(address).lstrip('0b').zfill(16)
    addressDL = str(hex(int('0b'+addressD[8:], base=2))).lstrip('0x').decode("hex") or b'\x00'
    addressDH = str(hex(int('0b'+addressD[:8], base=2))).lstrip('0x').decode("hex") or b'\x00'
    # print addressD, pretty_hex(addressDL), pretty_hex(addressDH)
    addressS = bin(253).lstrip('0b').zfill(16)
    addressSL = str(hex(int('0b'+addressS[8:], base=2))).lstrip('0x').decode("hex") or b'\x00'
    addressSH = str(hex(int('0b'+addressS[:8], base=2))).lstrip('0x').decode("hex") or b'\x00'
    # print addressS, pretty_hex(addressSL), pretty_hex(addressSH)
    message = OPT+addressDL+addressDH+addressSL+addressSH+pal
    crc8 = calc_crc(message)
    print pretty_hex(crc8)
    return END+message+crc8+END

def unpack_energy(message):
    energy = struct.unpack("<L", message[-6:-2])[0]/100.0
    return energy