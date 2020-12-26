class Interaction:
    def __init__(self, isBall, number,
                 accelerationX,
                 accelerationY,
                 jerkX, jerkY, jerkTheta,
                 entryNormal,
                 accelerationAngular,
                 stiffness):
        self.isBall = isBall
        self.number = number
        self.entryNormal = entryNormal
        self.accelerationX = accelerationX
        self.accelerationY = accelerationY
        self.jerkX = jerkX
        self.jerkY = jerkY
        self.jerkTheta = jerkTheta
        self.accelerationAngular = accelerationAngular
        self.stiffness = stiffness
        self.n = 1

    def changeAcceleration(self,
                           accelerationX,
                           accelerationY,
                           jerkX, jerkY, jerkTheta,
                           entryNormal,
                           accelerationAngular,
                           stiffness):
        self.accelerationX = accelerationX
        self.accelerationY = accelerationY
        self.jerkX = jerkX
        self.jerkY = jerkY
        self.jerkTheta = jerkTheta
        self.entryNormal = entryNormal
        self.accelerationAngular = accelerationAngular
        self.stiffness = stiffness
        self.n += 1
