import turtle, time, random

# pencere oluşturma
pencere = turtle.Screen()
pencere.title("Yılan Oyunu")
pencere.bgcolor("light blue")
pencere.setup(width=600, height=600)
pencere.tracer(0)

# yılanın başı
bas = turtle.Turtle()
bas.speed(0)
bas.shape("square")
bas.color("yellow")
bas.penup()
bas.goto(0, 100)
bas.direction = "stop"

# yem
yem = turtle.Turtle()
yem.speed(0)
yem.shape("circle")
yem.color("white")
yem.penup()
yem.goto(0, 0)
yem.shapesize(0.8, 0.8)

kuyruk = []
skor = 0

# skor tablosu
yaz = turtle.Turtle()
yaz.speed(0)
yaz.shape("square")
yaz.color("white")
yaz.penup()
yaz.goto(0, 260)
yaz.hideturtle()
yaz.write("Skor: {}".format(skor), align="center", font=("Courier", 24, "normal"))

# hareket fonksiyonu
def move():
    if bas.direction == "Up":
        bas.sety(bas.ycor() + 20)
    if bas.direction == "Down":
        bas.sety(bas.ycor() - 20)
    if bas.direction == "Right":
        bas.setx(bas.xcor() + 20)
    if bas.direction == "Left":
        bas.setx(bas.xcor() - 20)

# yön değiştirme fonksiyonları
def goUp():
    if bas.direction != "Down":
        bas.direction = "Up"
def goDown():
    if bas.direction != "Up":
        bas.direction = "Down"
def goRight():
    if bas.direction != "Left":
        bas.direction = "Right"
def goLeft():
    if bas.direction != "Right":
        bas.direction = "Left"

# oyunu sıfırla fonksiyonu
def oyunu_sifirla():
    global kuyruk, skor
    time.sleep(1)
    bas.goto(0, 0)
    bas.direction = "stop"
    for i in kuyruk:
        i.goto(1000, 1000)
    kuyruk.clear()
    skor = 0
    yaz.clear()
    yaz.write("Skor: {}".format(skor), align="center", font=("Courier", 24, "normal"))

# tuş dinleme
pencere.listen()
pencere.onkey(goUp, "Up")
pencere.onkey(goDown, "Down")
pencere.onkey(goRight, "Right")
pencere.onkey(goLeft, "Left")

# oyun döngüsü
while True:
    pencere.update()

    # duvara çarpma
    if bas.xcor() > 290 or bas.xcor() < -290 or bas.ycor() > 290 or bas.ycor() < -290:
        oyunu_sifirla()

    # kuyruğu takip ettirme (hareketten önce)
    for i in range(len(kuyruk) - 1, 0, -1):
        x = kuyruk[i - 1].xcor()
        y = kuyruk[i - 1].ycor()
        kuyruk[i].goto(x, y)

    if len(kuyruk) > 0:
        kuyruk[0].goto(bas.xcor(), bas.ycor())

    move()  # yılan başı hareket eder

    # kuyruğa çarpma kontrolü 
    if len(kuyruk) > 1:
        for parca in kuyruk:
            if parca.distance(bas) < 20:
                oyunu_sifirla()
                break

    # yemi yedi mi?
    if bas.distance(yem) < 20:
        x = random.randint(-250, 250)
        y = random.randint(-250, 250)
        yem.goto(x, y)

        skor += 10
        yaz.clear()
        yaz.write("Skor: {}".format(skor), align="center", font=("Courier", 24, "normal"))

        yeniKuyruk = turtle.Turtle()
        yeniKuyruk.speed(0)
        yeniKuyruk.shape("square")
        yeniKuyruk.color("red")
        yeniKuyruk.penup()
        yeniKuyruk.goto(1000, 1000)  # ekran dışı
        kuyruk.append(yeniKuyruk)
 

    time.sleep(0.12)
