from flask import Flask, url_for, request, render_template, jsonify, redirect
from markupsafe import escape
import json
import os
app = Flask(__name__)

file_path = "data.json"
file_2_path = "data_2.json"

def find_relation(word, array):
    founded = False
    founded_word = ""

    for index, row in enumerate(array):
        if row['id_relation'] == word:
            founded_word = row['tipe']
            founded = True
    
    if founded:
        return founded_word
    else:
        return "data tidak ditemukan"

@app.route('/', methods=['GET', 'POST'])
def index():
    import os

    # instansi variabel
    data = []
    new_data_2 = []
    data_2 = []
    keyword = ""
    columns = ['ID', 'Nama', 'Telepon', 'Tipe Mobil']
    columns_sort = ['id', 'nama', 'telepon', 'kode_relation']

    # data join dua tabel
    data_join = []

    # baca data.json, simpan di variabel data
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
    else:
        with open(file_path, "w") as file:
            json.dump([], file, indent=2)

    # baca data.json, simpan di variabel data
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_2_path):
        with open(file_2_path, "r") as file:
            data_2 = json.load(file)
    else:
        with open(file_2_path, "w") as file:
            json.dump([], file, indent=2)
    
    # copy without reference
    from copy import deepcopy
    data_join = deepcopy(data)  

    # looping semua data karyawan
    for index, row in enumerate(data_join):
        data_join[index]['tipe'] = find_relation(row['kode_relation'], data_2)

    # jika data dikiriim dengan method POST
    # maka update data karyawan di data.json
    if request.method == 'POST':
        keyword = request.form.get('keyword', '')
        sort_by = request.form.getlist('sort_by')

        # jika ada keyword,
        if keyword:
            for d in data_join:
                is_in_list = d['id'] == keyword or d['nama'].lower().find(keyword.lower()) != -1 or d['telepon'].find(keyword) != -1 or d['tipe'].lower().find(keyword.lower()) != -1
                if not is_in_list:
                    data_join.remove(d)
        elif sort_by:
            data_length = len(data_join) - 1
            # sorting data
            while (data_length > 0):
                index = 0
                while (index < data_length):
                    for by in sort_by:
                        if str(data_join[index][by]).casefold() > str(data_join[index + 1][by]).casefold():
                            temp = data_join[index]
                            data_join[index] = data_join[index + 1]
                            data_join[index+1] = temp
                    index += 1
                data_length -= 1
    
    # tampilkan data dengan template index.html
    return render_template('index.html', data=data_join, keyword=keyword, columns=columns, columns_sort=columns_sort)


@app.route('/tambah-data', methods=['GET', 'POST'])
def addData():
    new_data = {}
    data = []
    new_data_2 = []

    # baca data.json, simpan di variabel data
    with open(file_path, "r") as file:
        data = json.load(file)

    if request.method == 'POST':
        id = request.form.get('id', '')
        telepon = request.form.get('telepon', '')
        nama = request.form.get('nama', '')
        kode_relation = request.form.get('kode_relation', '')

        if id:
            new_data = {
                "id": id,
                "telepon": telepon,
                "nama": nama,
                "kode_relation": kode_relation
            }

            is_data_exist = any(d['id'] == id for d in data)
            # simpan ke variabel data karyawan baru
            if new_data and not is_data_exist:
                # data.append(new_data)
                new_data_2 = data + [new_data]

            # simpan ke variabel, data karyawan yang di edit
            else:
                # cari data sesuai 'id'
                for index, row in enumerate(data):
                    if row['id'] == id:
                        # ganti data di index sesuai id dengan data yang baru
                        data[index] = new_data
            
            # tulis ke file
            with open(file_path, "w") as file:
                # jika ada data baru, maka tulis new_data_2
                json.dump(
                    new_data_2 if new_data_2 else data, file, indent=2)

    add_done = True if new_data else False
    return render_template('add-data-form.html', data=new_data, add_done=add_done)


@app.route('/edit/<id>')
def editData(id):
    data = []

    # baca data.json, simpan di variabel data
    with open(file_path, "r") as file:
        data = json.load(file)

    # cari data sesuai 'id'
    for row in data:
        if row['id'] == id:
            data = row

    return render_template('add-data-form.html', data=data)


@app.route('/hapus/<id>')
def removeData(id):
    data = []
    deleted_data = {}
    deleted_index = 0

    # baca data.json, simpan di variabel data
    with open(file_path, "r") as file:
        data = json.load(file)

    # cari data sesuai id
    for index, row in enumerate(data):
        if row['id'] == id:
            # simpan data karyawan dan index yang akan dihapus
            deleted_data = row
            deleted_index = index
            # hentikan looping
            break

    if deleted_data:
        # ambil data kecuali yang sudah di hapus
        # mulai dari 0 sampai index data yang sudah di hapus
        # digabung dengan index + 1 data yang sudah di hapus sampai panjang data
        new_data_2 = data[0:deleted_index] + \
            data[deleted_index+1:len(data)]

        # tulis data setelah di hapus ke file
        with open(file_path, "w") as file:
            json.dump(new_data_2, file, indent=2)

    return render_template('remove-data.html', data=deleted_data)

@app.route('/tambah-data-relasi', methods=['GET', 'POST'])
def addData2():
    data_2 = []
    new_data = {}

    # baca data.json, simpan di variabel data
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_2_path):
        with open(file_2_path, "r") as file:
            data_2 = json.load(file)
    else:
        with open(file_2_path, "w") as file:
            json.dump([], file, indent=2)
    
    if request.method == 'POST':
        # untuk tambah data bagian
        id_relation = request.form.get('id_relation', '')
        tipe = request.form.get('tipe', '')

        if id_relation:
            new_data = {
                "id_relation": id_relation,
                "tipe": tipe
            }            
            is_data_exist = any(d['id_relation'] == id_relation for d in data_2)
            if new_data and not is_data_exist:
                data_2 = data_2 + [new_data]
             # simpan ke variabel, data karyawan yang di edit
            else:
                # cari data sesuai 'id'
                for index, row in enumerate(data_2):
                    if row['id_relation'] == id_relation:
                        # ganti data di index sesuai id dengan data yang baru
                        data_2[index] = new_data

            # tulis ke file
            with open(file_2_path, "w") as file:
                json.dump(data_2, file, indent=2)

    add_done = True if new_data else False
    return render_template('add-data-form-2.html', add_done=add_done)