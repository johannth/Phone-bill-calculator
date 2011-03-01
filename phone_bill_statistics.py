# -*- coding: utf-8 -*-
import os.path
from optparse import OptionParser
from datetime import datetime

NAME = -1
CALL_FAST_RATE = 0 
CALL_MINUTE_RATE = 1
SMS_PRICE = 2
MMS_PRICE = 3
COMPANY_NAME = 4

PHONE_COMPANIES = [
            { 
                COMPANY_NAME: 'Tal',
                NAME: 'Frelsi',
                CALL_FAST_RATE: 5.5,
                CALL_MINUTE_RATE: 12.5,
                SMS_PRICE: 10,
                MMS_PRICE: 15,
            },
            { 
                NAME: 'Vinakerfi',
                CALL_FAST_RATE: 5.5,
                CALL_MINUTE_RATE: 15.5,
                SMS_PRICE: 11,
                MMS_PRICE: 15,
            },
            {
                COMPANY_NAME: 'Nova',
                NAME: '0 kr. Nova i Nova',
                CALL_FAST_RATE: 5.9,
                CALL_MINUTE_RATE: 18.9,
                SMS_PRICE: 9.9,
                MMS_PRICE: 9.9
            },
            {
                COMPANY_NAME: 'Nova',
                NAME: 'Eitt verð i alla',
                CALL_FAST_RATE: 5.9,
                CALL_MINUTE_RATE: 9.9,
                SMS_PRICE: 9.9,
                MMS_PRICE: 9.9
            }]



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
         
    column_names = ['"Símanúmer"','"Nafn"','"Er heimasími"','"Fjöldi MMS-a"','"Fjöldi SMS-a"','"Fjöldi símtala"','"Sekúndur"','"Kostnaður (ISK)"']
    column_names.extend(['"%s - %s"' % (x[COMPANY_NAME], x[NAME]) for x in PHONE_COMPANIES])
    output_file = open(filename, "w")
    output_file.write(",".join(column_names))
    output_file.write("\n") 
    for phonenumber, phonenumber_stats in phonenumbers.iteritems():
        mms_count = phonenumber_stats["mms_count"]
        sms_count = phonenumber_stats["sms_count"]
        call_count = phonenumber_stats["call_count"]
        cost = phonenumber_stats["cost"]
        seconds = phonenumber_stats["seconds"]
        is_landline = str(phonenumber).startswith("4") or str(phonenumber).startswith("5")
        
        new_costs = []
        for company_rate in PHONE_COMPANIES:
            new_cost = calculate_cost_for_company(company_rate, sms_count, mms_count, seconds, call_count)
            new_costs.append(new_cost)
            

        columns = [phonenumber, "", int(is_landline), mms_count, sms_count, call_count, seconds, cost]
        columns.extend(new_costs)
        output_file.write(",".join(str(x) for x in columns))
        output_file.write("\n")   
        
def calculate_cost_for_company(company_rate, sms_count, mms_count, seconds, call_count):
    return sms_count * company_rate[SMS_PRICE] + mms_count * company_rate[MMS_PRICE] + seconds / 60.0 * company_rate[CALL_MINUTE_RATE] + call_count * company_rate[CALL_FAST_RATE]


if __name__ == "__main__":
    parser = OptionParser()
    (options, args) = parser.parse_args()
    
    generate_statistics(args[0])
    