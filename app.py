from flask import Flask, render_template,request,redirect,url_for,flash
#import video_stop
import videoopencv

app = Flask(__name__)

# Settings
app.secret_key='mysecretkey'

@app.route('/')

def index():
    return render_template('index.html')



@app.route('/run',methods=['POST'])
def run():
    if request.method == 'POST':
        cama=request.form['cama']
        bloque=request.form['bloque']
        date=request.form['date']
        if  len(str(cama))==0 or len(str(bloque))==0 or len(str(date))==0:
            print('faltan datos')
            return redirect(url_for('index')) 
        #print(data)
    f=videoopencv.take_video(cama,bloque,date) 
    return render_template('run.html',data=f)

@app.route('/back')

def backtomain():
    return 'Volver'

if __name__ == '__main__':
    app.run(port=3000,debug=True)
    