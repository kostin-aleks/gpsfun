#!/usr/bin/env python
# -*- coding: utf-8 -*-
ABC = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

def char2digit(ch):
    k = 0
    for char in ABC:
        k += 1
        if char == ch:
            return str(k)
    return 'NONE'

def main():
    

    streets = [
        'ольминскогофрунзе',
        'петровскогогиршмана',
        'краснознамённаячайковская',
        'красина',
        'студенческая',
        'маршалабажанова',
        'иванова',
        'дарвина',
        'лермонтовская',
        'гуданова',
    ]
    
    for street in streets:
        print street
        print [ord(ch)-ord('а'[0]) for ch in street]
        print ''.join([char2digit(ch) for ch in street])
        print

if __name__ == '__main__':
    main()
