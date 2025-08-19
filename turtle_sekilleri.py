import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.srv import Spawn, SetPen, TeleportAbsolute
import math, time, threading

# Hız ayarları
LIN_HIZ = 4.0      # m/s
ANG_HIZ = 0.325    # rad/s
FREKANS = 60       # Hz

class Kaplumbagalar(Node):
    def __init__(self):
        super().__init__('kaplumbagalar')

        # Kaplumbağaların özellikleri
        self.kaplumbagalar = {
            'turtle1': {'sekil': 'ucgen',    'uzunluk': 2.2, 'pos': (1.5, 8.5, 0.0)},
            'turtle2': {'sekil': 'kare',     'uzunluk': 2.0, 'pos': (8.0, 8.5, 0.0)},
            'turtle3': {'sekil': 'besgen',   'uzunluk': 2.0, 'pos': (1.5, 1.0, 0.0)},
            'turtle4': {'sekil': 'altigen',  'uzunluk': 1.8, 'pos': (8.0, 1.0, 0.0)},
            'turtle5': {'sekil': 'yildiz',   'uzunluk': 3.0, 'pos': (4.5, 5.5, 0.0)},
        }

        self.pub_map = {}

        # Spawn servisi
        self.spawn_cli = self.create_client(Spawn, '/spawn')
        while not self.spawn_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('spawn servisi bekleniyor...')

        # Turtle1 var → teleport
        self.teleport('turtle1', *self.kaplumbagalar['turtle1']['pos'])

        # Yeni kaplumbağalar
        for ad in ['turtle2', 'turtle3', 'turtle4', 'turtle5']:
            x, y, th = self.kaplumbagalar[ad]['pos']
            req = Spawn.Request()
            req.x, req.y, req.theta, req.name = float(x), float(y), float(th), ad
            fut = self.spawn_cli.call_async(req)
            rclpy.spin_until_future_complete(self, fut)

        # Publisher’lar
        for ad in self.kaplumbagalar.keys():
            self.pub_map[ad] = self.create_publisher(Twist, f'/{ad}/cmd_vel', 10)
        time.sleep(0.2)

        # Kalem renkleri
        kalemler = {
            'turtle1': (255, 0,   0,   3),
            'turtle2': (0,   180, 0,   3),
            'turtle3': (30,  144, 255, 3),
            'turtle4': (180, 0,   180, 3),
            'turtle5': (20,  20,  20,  3),
        }
        for ad, (r, g, b, w) in kalemler.items():
            self.set_pen(ad, r, g, b, w, off=0)

        self.barrier = threading.Barrier(len(self.kaplumbagalar) + 1)

    # --- Servis yardımcıları ---
    def cagir(self, srv_type, name, req):
        cli = self.create_client(srv_type, name)
        while not cli.wait_for_service(timeout_sec=1.0):
            pass
        fut = cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)

    def teleport(self, ad, x, y, theta):
        self.set_pen(ad, 0, 0, 0, 1, off=1)
        req = TeleportAbsolute.Request()
        req.x, req.y, req.theta = float(x), float(y), float(theta)
        self.cagir(TeleportAbsolute, f'/{ad}/teleport_absolute', req)
        time.sleep(0.05)

    def set_pen(self, ad, r, g, b, w, off=0):
        req = SetPen.Request()
        req.r, req.g, req.b, req.width, req.off = int(r), int(g), int(b), int(w), int(off)
        self.cagir(SetPen, f'/{ad}/set_pen', req)
        time.sleep(0.02)

    # --- Hareket ---
    def hareket_et(self, ad, vx, wz, sure):
        pub = self.pub_map[ad]
        msg = Twist()
        bitis = time.time() + sure
        dt = 1.0 / FREKANS
        while time.time() < bitis:
            msg.linear.x, msg.angular.z = vx, wz
            pub.publish(msg)
            time.sleep(dt)
        msg.linear.x = msg.angular.z = 0.0
        pub.publish(msg)
        time.sleep(0.02)

    def ileri_git(self, ad, uzunluk):
        self.hareket_et(ad, LIN_HIZ, 0.0, float(uzunluk) / LIN_HIZ)

    def don(self, ad, derece):
        rad = math.radians(derece)
        sure = abs(rad) / ANG_HIZ
        wz = ANG_HIZ if rad >= 0 else -ANG_HIZ
        self.hareket_et(ad, 0.0, wz, sure)

    # --- Şekiller ---
    def duzgun_cokgen(self, ad, kenar_sayisi, uzunluk):
        aci = 360.0 / float(kenar_sayisi)
        for _ in range(kenar_sayisi):
            self.ileri_git(ad, uzunluk)
            self.don(ad, aci)

    def yildiz(self, ad, uzunluk):
        for _ in range(5):
            self.ileri_git(ad, uzunluk)
            self.don(ad, 144.0)

    def worker(self, ad, ozellik):
        self.barrier.wait()
        sekil, L = ozellik['sekil'], ozellik['uzunluk']
        if sekil == 'ucgen':     self.duzgun_cokgen(ad, 3, L)
        elif sekil == 'kare':    self.duzgun_cokgen(ad, 4, L)
        elif sekil == 'besgen':  self.duzgun_cokgen(ad, 5, L)
        elif sekil == 'altigen': self.duzgun_cokgen(ad, 6, L)
        elif sekil == 'yildiz':  self.yildiz(ad, L)

def main(args=None):
    rclpy.init(args=args)
    node = Kaplumbagalar()

    ths = []
    for ad, ozellik in node.kaplumbagalar.items():
        t = threading.Thread(target=node.worker, args=(ad, ozellik), daemon=True)
        ths.append(t); t.start()

    node.barrier.wait()

    for t in ths:
        t.join()

    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
