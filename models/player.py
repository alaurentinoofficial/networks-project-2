class Player():
    ip: str
    port: int
    points: float
    name: str

    def __init__(self, ip: str, port: int, name: str, points: float = 0.0):
        self.ip = ip
        self.port = port
        self.points = points
        self.name = name
    
    def __str__(self):
        return f"Player(ip={self.ip}, port={self.port}, name={self.name}, points={self.points})"
    
    def __repr__(self):
        return f"Player(ip={self.ip}, port={self.port}, name={self.name}, points={self.points})"

    @property
    def address(self):
        return f"{self.ip}:{self.port}"

    def __eq__(self, other):
        if isinstance(other, Player):
            return self.address == other.address
        elif type(other) is str:
            return self.address == other
        else:
            return False