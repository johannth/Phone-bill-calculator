# -*- coding: utf-8 -*-
import os.path
from optparse import OptionParser
from datetime import datetime

CALL_FAST_RATE = 5.5
CALL_MINUTE_RATE = 12.5
SMS_PRICE = 10
MMS_PRICE = 15

def generate_statistics(datafile_path):
    path, filename = os.path.split(datafile_path)
    datafile = open(datafile_path, "r")
    
    phonenumbers = {}
    for line in datafile:
        date, call_type, phonenumber, duration_malformed, price = line.split(";")
        try:
            phonenumber = int(phonenumber)
        except ValueError:
            continue
        
        if len(str(phonenumber)) != 7:
            continue

        is_sms = call_type == "\"SMS\""
        is_mms = call_type == "\"MMS\""
        sms_error = call_type.startswith("\"Bak")

        phonenumber_stats = phonenumbers.get(phonenumber, {'seconds': 0, 'mms_count': 0, 'sms_count': 0, 'call_count': 0, 'cost': 0})
        
        if not (is_sms or is_mms) and not sms_error:
            duration_as_int = int(duration_malformed.replace(":", "").replace("AM", "").strip())
            duration_as_int = duration_as_int - 120000
            
            duration_as_string = str(duration_as_int)
            seconds = duration_as_string[-2:] or 0
            minutes = duration_as_string[-4:-2] or 0
            hours = duration_as_string[-6:-4] or 0
            
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
            phonenumber_stats["seconds"] += hours * (60 * 60) + minutes * 60 + seconds
        

        if is_sms:
            phonenumber_stats["sms_count"] += 1
        elif is_mms:
            phonenumber_stats["mms_count"] += 1
        elif sms_error:
            phonenumber_stats["sms_count"] -= 1
        else:
            phonenumber_stats["call_count"] += 1
            
        price = float(price.replace("\"", "").replace("kr.", "").replace(",",".").strip())
        
        phonenumber_stats["cost"] += price
        
        phonenumbers[phonenumber] = phonenumber_stats
        
   
        
    output_file = open(filename, "w")
    output_file.write('"Símanúmer","Nafn","Er heimasími","Fjöldi MMS-a","Fjöldi SMS-a","Fjöldi símtala","Sekúndur","Kostnaður (ISK)", "Kostnaður ef þú ferð í Tal"\n')
    for phonenumber, phonenumber_stats in phonenumbers.iteritems():
        mms_count = phonenumber_stats["mms_count"]
        sms_count = phonenumber_stats["sms_count"]
        call_count = phonenumber_stats["call_count"]
        cost = phonenumber_stats["cost"]
        seconds = phonenumber_stats["seconds"]
        new_cost = sms_count * SMS_PRICE + mms_count * MMS_PRICE + seconds / 60.0 * CALL_MINUTE_RATE + call_count * CALL_FAST_RATE
        is_landline = str(phonenumber).startswith("4") or str(phonenumber).startswith("5")
        
        output_file.write(",".join(str(x) for x in [phonenumber, "", int(is_landline), mms_count, sms_count, call_count, seconds, cost, new_cost]))
        output_file.write("\n")   

if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    
    generate_statistics(args[0])
    