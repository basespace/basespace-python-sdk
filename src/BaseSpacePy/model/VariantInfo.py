#!/usr/bin/env python

class VariantInfo:
    def __init__(self):
        self.swaggerTypes = {
            'CIGAR': 'list<Str>',
            'IDREP': 'list<Str>',                 
            'REFREP': 'list<Str>',
            'RU':'list<Str>',
            'VARTYPE_DEL':'list<Str>',
            'VARTYPE_INS':'list<Str>',
            'VARTYPE_SNV':'list<Str>',
        }
        
        self.CIGAR          = None
        self.IDREP          = None
        self.REFREP         = None
        self.RU             = None
        self.VARTYPE_DEL    = None
        self.VARTYPE_INS    = None
        self.VARTYPE_SNV    = None
 