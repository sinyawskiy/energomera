# -*- coding: utf-8 -*-
import socket
from energomera.protocol import get_ping, unpack_energy, get_energy, GET_ENERGY_SUM, GET_ENERGY_TARIF1, GET_ENERGY_TARIF2, GET_ENERGY_TARIF3, GET_ENERGY_TARIF4, GET_ENERGY_TARIF5
from energomera.utils import pretty_hex

HOST = '192.168.153.195'
PORT = 5010
ADDRESS_ENERGOMERA = 27268 # последние 5 символов серийного номера

TIMEOUT = 5 #energomera 2000ms

def readDataFromSocket(s):
    data = ''
    buffer = ''
    try:
        while True:
            s.settimeout(TIMEOUT)
            data = s.recv(1)
            if data:
                buffer += data
                s.settimeout(None)
    except Exception, error:
        print 'Error', error

    # print pretty_hex(buffer)
    s.settimeout(None)
    return buffer


def send_ping_command(s, *params, **kwargs):
    ping = get_ping(ADDRESS_ENERGOMERA)
    print '>> ', pretty_hex(ping)
    s.sendall(ping)
    answer = readDataFromSocket(s)
    answer_lines = answer.split('\r\n')
    answer = ''.join(answer_lines)
    print '<< ', pretty_hex(answer)


def send_tcp_command(s, *params, **kwargs):
    result = []
    for energy_data in [GET_ENERGY_SUM, GET_ENERGY_TARIF1, GET_ENERGY_TARIF2, GET_ENERGY_TARIF3, GET_ENERGY_TARIF4, GET_ENERGY_TARIF5]:
        message = get_energy(energy_data, ADDRESS_ENERGOMERA)
        print '>> ', pretty_hex(message)
        s.sendall(message)
        answer = readDataFromSocket(s)
        answer_lines = answer.split('\r\n')
        answer = ''.join(answer_lines)
        print '<< ',pretty_hex(answer)
        result.append(unpack_energy(answer))
    return result


if __name__== "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    # send_ping_command(s)
    readings = send_tcp_command(s)
    print readings

