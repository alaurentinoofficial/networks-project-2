
class Player():
    ip: str
    port: int
    point: float

    def __init__(self, ip: str, port: int, point: float = 0.0):
        self.ip = ip
        self.port = port
        self.point = point
    
    def __str__(self):
        return f"Player(ip={self.ip}, port={self.port}, points={self.point})"
    
    def __repr__(self):
        return f"Player(ip={self.ip}, port={self.port}, points={self.point})"
