import re
import csv
import codecs
from flask import Flask,render_template,request,jsonify

app = Flask(__name__)

Year = "2019"
fail_list = []
all_list = []
log_list = []
log_map = {}

def analyse_csv(csv_file):
    fail_list.clear()
    all_list.clear()
    reader = csv.DictReader(codecs.iterdecode(csv_file,"utf-8"))
    for item in reader:
        Dict = {}
        timestamp = "{}-{}-{} {}:{}:{}.{}".format(Year,item['month'],item['day'],item['hour'],item['minute'],item['second'],item['microsec'])
        low_high_unit = "{}~{} {}".format(item['low'],item['high'],item['unit'])
        Dict['timestamp'] = timestamp
        Dict['low_high_unit'] = low_high_unit
        Dict['result'] = item['result']
        Dict['value'] = item['value']
        Dict['sn'] = item['sn']
        Dict['group'] = item['group']
        Dict['tid'] = item['tid']
        Dict['year'] = Year
        Dict['month'] = item['month']
        Dict['day'] = item['day']
        Dict['hour'] = item['hour']
        Dict['minute'] = item['minute']
        Dict['second'] = item['second']
        all_list.append(Dict)
        if item['result'] == 'Fail':
            fail_list.append(Dict)

def analyse_log(log_file):
    log_list.clear()
    log_map.clear()
    pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d+'
    log = codecs.iterdecode(log_file[1], "utf-8")
    item = ""
    for line in log:
        m = re.match(pattern, line)
        if m:
            item += line
            log_list.append((m.group(),item))
            log_map[m.group()] = item
            item = ""
        else:
            item += line

@app.route('/log')
def getlog():
    if log_map:
        utime = request.args.get("timestamp")
        if utime and utime in log_map:
            return jsonify({
                "code":1,
                "msg": "sucess",
                "log":log_map[utime]
            })
        return jsonify({
            "code": 0,
            "msg": "timestamp not in log",
            "log": ""
        })
    else:
        return jsonify({
            "code": 0,
            "msg": "log not detected,please upload again",
            "log": ""
        })

@app.route('/',methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        csv_file = request.files.get("csv")
        length = request.args.get("length")
        log_file = []
        log_file.clear()
        for i in range(length):
            log_file.append(request.files.get("log{}".format(i)))
        # if uploaed file, process the file and then return the required lists
        if csv_file.filename.endswith("csv") and log_file[0].filename.endswith("log"):
            analyse_log(log_file)
            analyse_csv(csv_file)
            return jsonify({
                "code": 1,
                "msg": "sucess",
                "fail": fail_list,
                "all": all_list,
                "log": log_list
            })
        # if no right file was uploaded, return the lists with empty content
        return jsonify({
            "code": 0,
            "msg": "filename suffix error",
            "fail":[],
            "all":[],
            "log": []
        })

if __name__ == '__main__':
    app.run(debug=True)
