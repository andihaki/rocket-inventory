from flask import Flask, url_for, request, render_template, jsonify, redirect
from markupsafe import escape
app = Flask(__name__)

file_path = "data.json"
file_2_path = "data_bagian.json"

def find_relation(word, array):
    founded = False
    founded_word = ""

    for index, row in enumerate(array):
        if row['kode_bagian'] == word:
            founded_word = row['nama_bagian']
            founded = True
    
    if founded:
        return founded_word
    else:
        return "data tidak ditemukan"

@app.route('/', methods=['GET', 'POST'])
def index():
    import json
    import os

    # instansi variabel
    data_karyawan = []
    new_data_karyawan = []
    data_bagian = []
    new_data_bagian = []
    keyword = ""
    columns = ['NIP', 'Golongan', 'Nama', 'Nama Bagian']
    columns_sort = ['nip', 'golongan', 'nama', 'nama_bagian']

    # data join dua tabel
    data_join = []

    # baca data.json, simpan di variabel data_karyawan
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_path):
        with open(file_path, "r") as file:
            data_karyawan = json.load(file)
    else:
        with open(file_path, "w") as file:
            json.dump([], file, indent=2)

    # baca data.json, simpan di variabel data_karyawan
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_2_path):
        with open(file_2_path, "r") as file:
            data_bagian = json.load(file)
    else:
        with open(file_2_path, "w") as file:
            json.dump([], file, indent=2)
    
    # copy without reference
    from copy import deepcopy
    data_join = deepcopy(data_karyawan)  

    # looping semua data karyawan
    for index, row in enumerate(data_join):
        data_join[index]['nama_bagian'] = find_relation(row['kode_bagian'], data_bagian)

    # baca data.json, simpan di variabel data_karyawan
    # jika file tidak ada, maka buat file tersebut
    if os.path.exists(file_2_path):
        with open(file_2_path, "r") as file:
            data_bagian = json.load(file)
    else:
        with open(file_2_path, "w") as file:
            json.dump([], file, indent=2)

    # jika data dikiriim dengan method POST
    # maka update data karyawan di data.json
    if request.method == 'POST':
        nip = request.form.get('nip', '')
        golongan = request.form.get('golongan', '')
        nama = request.form.get('nama', '')
        kode_bagian = request.form.get('kode_bagian', '')
        keyword = request.form.get('keyword', '')
        sort_by = request.form.getlist('sort_by')

        # untuk tambah data bagian
        nama_bagian = request.form.get('nama_bagian', '')

        # jika ada keyword,
        if keyword:
            for data in data_karyawan:
                if data['nip'] == keyword:
                    data_karyawan = [data]

                    break
                else:
                    data_karyawan = []
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

        elif nip:
            new_data = {
                "nip": nip,
                "golongan": golongan,
                "nama": nama,
                "kode_bagian": kode_bagian
            }

            is_data_exist = any(d['nip'] == nip for d in data_karyawan)
            # simpan ke variabel data karyawan baru
            if new_data and not is_data_exist:
                # data_karyawan.append(new_data)
                new_data_karyawan = data_karyawan + [new_data]

            # simpan ke variabel, data karyawan yang di edit
            else:
                # cari data sesuai 'id'
                for index, row in enumerate(data_karyawan):
                    if row['nip'] == nip:
                        # ganti data di index sesuai nip dengan data yang baru
                        data_karyawan[index] = new_data
            # data_karyawan = new_data_karyawan
            
            # tulis ke file
            with open(file_path, "w") as file:
                # jika ada data baru, maka tulis new_data_karyawan
                json.dump(
                    new_data_karyawan if new_data_karyawan else data_karyawan, file, indent=2)
        
        elif kode_bagian:
            new_data = {
                "kode_bagian": kode_bagian,
                "nama_bagian": nama_bagian
            }
            is_data_exist = any(d['kode_bagian'] == kode_bagian for d in data_bagian)
            if new_data and not is_data_exist:
                new_data_bagian = data_bagian + [new_data]
            data_bagian = new_data_bagian

            # tulis ke file
            with open(file_2_path, "w") as file:
                json.dump(new_data_bagian if new_data_bagian else data_bagian, file, indent=2)
        
        # refresh page
        redirect(url_for('index'))

    
    # tampilkan data_karyawan dengan template index.html
    return render_template('index.html', data=data_join, keyword=keyword, columns=columns, columns_sort=columns_sort)


@app.route('/tambah-data-karyawan')
def addData():
    return render_template('add-data-form.html')


@app.route('/edit/<id>')
def editData(id):
    data_karyawan = []

    # baca data.json, simpan di variabel data_karyawan
    with open(file_path, "r") as file:
        import json
        data_karyawan = json.load(file)

    # cari data sesuai 'id'
    for row in data_karyawan:
        if row['nip'] == id:
            data_karyawan = row

    return render_template('add-data-form.html', data=data_karyawan)


@app.route('/hapus/<id>')
def removeData(id):
    data_karyawan = []
    deleted_data = {}
    deleted_index = 0

    # baca data.json, simpan di variabel data_karyawan
    with open(file_path, "r") as file:
        import json
        data_karyawan = json.load(file)

    # cari data sesuai id
    for index, row in enumerate(data_karyawan):
        if row['nip'] == id:
            # simpan data karyawan dan index yang akan dihapus
            deleted_data = row
            deleted_index = index
            # hentikan looping
            break

    if deleted_data:
        # ambil data kecuali yang sudah di hapus
        # mulai dari 0 sampai index data yang sudah di hapus
        # digabung dengan index + 1 data yang sudah di hapus sampai panjang data
        new_data_karyawan = data_karyawan[0:deleted_index] + \
            data_karyawan[deleted_index+1:len(data_karyawan)]

        # tulis data setelah di hapus ke file
        with open(file_path, "w") as file:
            json.dump(new_data_karyawan, file, indent=2)

    return render_template('remove-data.html', data=deleted_data)

@app.route('/tambah-data-bagian')
def addData2():
    return render_template('add-data-form-2.html')