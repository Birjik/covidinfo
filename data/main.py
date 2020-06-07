import os
import math
import csv

#os.system("cd COVID-19/csse_covid_19_data/csse_covid_19_time_series && git pull && cd .. && cd .. && cd ..")

f_confirmed = open("COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv", "r")
dict_confirmed = csv.DictReader(f_confirmed, delimiter=',')

f_recovered = open("COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv", "r")
dict_recovered = csv.DictReader(f_recovered)

f_deaths = open("COVID-19/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv", "r")
dict_deaths = csv.DictReader(f_deaths)

res = {}
res2 = {}
dmy = []
newdmy = []

def data_conv(init):
    return init[0] + "-" + init[1] + "-" + init[2]


dic = {}
with open("wikipedia-iso-country-codes.csv") as f:
    file= csv.DictReader(f, delimiter=',')
    for line in file:
        dic[line['English short name lower case']] = line['Alpha-2 code']

countries2 = {
    "West Bank and Gaza" : "",
    "Kosovo" : "",
    "MS Zaandam" : "",
}

def country_conv(init):
    if init in dic:
        return dic[init]
    if len(init) == 2:
        return init

    return "";

def cases_conv(init):
    if init < 1:
        return init
    if init < 100:
        return 0.1
    if init < 1000:
        return 3 + init * 6 / 1000
    if init < 10000:
        return 10 + init / (10000/140)
    if init < 100000:
        return 300 + init / (100000/1200)
    if init < 1000000:
        return 2000 + init / (1000000/1000)
    return 6000 + init / (5000000/9000)

first = 0
for line in dict_confirmed:
    if first == 0:
        first = 1
        for key in line:
            if key[-1] == '0' or key[-1] == '9':
                dmy.append(key)
                newdmy.append(key.split("/"))
                newdmy[-1].reverse()
                newdmy[-1][0] = "20" + newdmy[-1][0]
                newdmy[-1][1], newdmy[-1][2] = newdmy[-1][2].zfill(2), newdmy[-1][1].zfill(2)
    for i in range(len(dmy)):
        if data_conv(newdmy[i]) in res2:
            if line["Province/State"] == "Falkland Islands (Malvinas)":
                line["Country/Region"] = "FK"
            if line["Country/Region"] in res2[data_conv(newdmy[i])]:
                res2[data_conv(newdmy[i])][line["Country/Region"]]["confirmed"] += int(line[dmy[i]]);
            else:
                res2[data_conv(newdmy[i])][line["Country/Region"]] = {"confirmed" : int(line[dmy[i]])};
        else:
            res2[data_conv(newdmy[i])] = {line["Country/Region"]: {"confirmed" : int(line[dmy[i]])}}
            res2[data_conv(newdmy[i])][line["Country/Region"]]["confirmed"] = int(line[dmy[i]]);

for line in dict_recovered:
    for i in range(len(dmy)):
        if line["Province/State"] == "Falkland Islands (Malvinas)":
            line["Country/Region"] = "FK"
        if "recovered" in res2[data_conv(newdmy[i])][line["Country/Region"]]:
            res2[data_conv(newdmy[i])][line["Country/Region"]]["recovered"] += int(line[dmy[i]]);
        else:
            res2[data_conv(newdmy[i])][line["Country/Region"]]["recovered"] = int(line[dmy[i]]);

for line in dict_deaths:
    for i in range(len(dmy)):
        if line["Province/State"] == "Falkland Islands (Malvinas)":
            line["Country/Region"] = "FK"
        if "deaths" in res2[data_conv(newdmy[i])][line["Country/Region"]]:
            res2[data_conv(newdmy[i])][line["Country/Region"]]["deaths"] += int(line[dmy[i]]);
        else:
            res2[data_conv(newdmy[i])][line["Country/Region"]]["deaths"] = int(line[dmy[i]]);

bigdata = open("bigdata.js", "w", newline = '')

chart = {}
chartActive = {}

for (data, val1) in res2.items():
    bigdata.write("<script src='./data/result/" + data + ".js'></script>\n");
    new_data = open("result/" + data + ".js", "w", newline = '')

    #write data[] = {}

    new_data.write("data[\"" + data + "\"] = {\"TF\": 15000");
    for (country, val2) in val1.items():
        if len(country_conv(country)) == 0:
            continue
        new_data.write("\n,")
        new_data.write("\"" + country_conv(country) + "\": " + str(cases_conv(val2["confirmed"])))
    new_data.write("\n}\n")

    #write dataActive[] = {}

    new_data.write("dataActive[\"" + data + "\"] = {\"TF\": 15000");
    last = 0
    for (country, val2) in val1.items():
        if len(country_conv(country)) == 0:
            continue
        new_data.write("\n,")
        new_data.write("\"" + country_conv(country) + "\": " + str(cases_conv(val2["confirmed"]-val2["deaths"]-val2["recovered"])))
        last = val2["confirmed"]
    new_data.write("\n}\n")

    #write info[] = {}

    new_data.write("info[\"" + data + "\"] = {\"temp\": 0");
    WORLDconfirmed = 0
    WORLDrecovered = 0
    WORLDdeaths = 0
    for (country, val2) in val1.items():
        if len(country_conv(country)) == 0:
            continue
        new_data.write("\n,")
        new_data.write("\"" + country_conv(country) + "confirmed\": " + str(val2["confirmed"]))
        if country_conv(country) in chart:
            chart[country_conv(country)][data] = str(val2["confirmed"])
        else:
            chart[country_conv(country)] = {data : str(val2["confirmed"])}
        if country_conv(country) in chartActive:
            chartActive[country_conv(country)][data] = str(val2["confirmed"] - val2["deaths"] - val2["recovered"])
        else:
            chartActive[country_conv(country)] = {data : str(val2["confirmed"] - val2["deaths"] - val2["recovered"])}
        new_data.write(", \"" + country_conv(country) + "recovered\": " + str(val2["recovered"]))
        new_data.write(", \"" + country_conv(country) + "deaths\": " + str(val2["deaths"]))
        WORLDconfirmed += val2["confirmed"]
        WORLDrecovered += val2["recovered"]
        WORLDdeaths += val2["deaths"]

    if "WORLD" in chart:
        chart["WORLD"][data] = str(WORLDconfirmed)
    else:
        chart["WORLD"] = {data : str(WORLDconfirmed)}
    if "WORLD" in chartActive:
        chartActive["WORLD"][data] = str(WORLDconfirmed - WORLDdeaths - WORLDrecovered)
    else:
        chartActive["WORLD"] = {data : str(WORLDconfirmed - WORLDdeaths - WORLDrecovered)}

    new_data.write("\n,\"" + "WORLDconfirmed\": " + str(WORLDconfirmed))
    new_data.write(", \"" + "WORLDrecovered\": " + str(WORLDrecovered))
    new_data.write(", \"" + "WORLDdeaths\": " + str(WORLDdeaths))
    new_data.write("\n}")
    new_data.close()

bigdata.close()
# write charts.js

charts = open("charts.js", "w", newline = '')

def conv_data_without(init):
    return init[0:4] + init[5:7] + init[8:]


for (country, val1) in chart.items():
    last = 0
    charts.write("charts[\"" + country + "\"] = \",\\n\" + ")
    for (data, res) in val1.items():
        charts.write("\"" + conv_data_without(data) + "," + str(max(0, int(res) - last)) + "\\n\" + ")
        last = int(res)
    charts.write("\"\";\n")
charts.close()

chartsActive = open("chartsActive.js", "w", newline = '')

for (country, val1) in chartActive.items():
    chartsActive.write("chartsActive[\"" + country + "\"] = \",\\n\" + ")
    for (data, res) in val1.items():
        chartsActive.write("\"" + conv_data_without(data) + "," + str(int(res)) + "\\n\" + ")
    chartsActive.write("\"\";\n")
chartsActive.close()
