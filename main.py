import math
import cmath
#from turtle import *
import numpy as np
import scipy
import matplotlib.pyplot as plt
import multiprocessing as mp
"""
main
===========================

Set the parameters gamma, delta, epsilon here. This will dictate what Heun Equation is utilized in the simulation.
"""
gamma = complex(1/2,0)
delta = complex(3/4,0)
epsilon = complex(1/4,0)
alpha = (gamma+delta+epsilon-1)/2
beta = alpha

radius = .4
time = 0
speed = .00005
deltax = complex(0,0)

d2y = complex(0,0) # y''
dy = complex(0,0) # y'
y = complex(1,0)


x = complex(radius,0)
a = complex(-1,0) #

B_init = complex(11,8) # q = B/4
center = 0
#turtle = Turtle()
#screen = turtle.getscreen()
#screen.tracer(20)

bees = []

#Common point that all paths go through:
p = complex(1,1)

"""
Update Functions
===========================

The following functions simply iterate the values of x, y, and the derivatives of y and are used in the monodromy simulation.
"""
def update_d2Y(B):
    global d2y
    d2y = -(gamma/x+delta/(x-1)+epsilon/(x-a))*dy - ((alpha*beta*x-B/4)/(x*(x-1)*(x-a)))*y

def update_dY():
    global dy
    dy += deltax*d2y

def update_Y():
    global y
    y += deltax*dy

def update_x():
    global x, deltax, time, center
    time = speed + time
    last_x = x
    if time < 1:
        x = x + ((center + radius) - p) * speed
    elif time >= 1 and time < 2:
        x = radius * cmath.exp(time * complex(0, math.pi * 2)) + center
    elif time >= 2:
        x = x + (p - (center + radius)) * speed
    deltax = x - last_x
   # turtle.goto(x.real*100, x.imag*100)
def update(B):
    update_x()
    update_d2Y(B)
    update_dY()
    update_Y()
def simulate(B):
    """
    Simulate
    ===========================

    Uses the Update Functions defined above to simulate a monodromy around the pole defined by the variable 'center' of the Heun Equation.

    Parameters:
    -----------
    none (all parameters of the Heun Equation are set in the Update Functions and in the global variables previously defined).

    Returns:
    -----------
    The monodromy matrix around the 'center' pole, as a numpy array.
    """
    global x, time, d2y, dy, y
    #print("started")
    d2y = 0
    dy = complex(0, 0)  # y'
    y = complex(1, 0)
    time = 0
    x = p
    while time < 3:
        update(B)
    a = y
    c = dy

    d2y = 0
    dy = complex(1, 0)  # y'
    y = complex(0, 0)
    time = 0
    x = p
    while time < 3:
        update(B)
    b = y
    d = dy

    return np.matrix([[a,c],[b,d]])

def findMatrices(B):
    """
    findMatrices
B    ===========================

    Uses the Simulate function to find all monodromy matrices of the Heun Equation.

    Parameters:
    -----------
    none (all parameters of the Heun Equation are set in the Update Functions and in the global variables previously defined).

    Returns:
    -----------
    The monodromy matrices around the poles at 0, 1, and the variable a.
    """
    global center, x
    #Record around 0
    x = complex(radius,0) + 0
    center = 0
    M0 = simulate(B)
    #print(M0)
    #Record around 1
    center = 1
    x = complex(radius,0)+ 1
    M1 = simulate(B)
    #print(M1)
    #Record around a
    center = a
    x = complex(radius,0) + a
    Ma = simulate(B)
    #print(Ma)
    return M0, M1, Ma

#M0, M1, Ma = findMatrices(B)
#M = M0 * M1 * Ma
#print(np.linalg.eigvals(M))
#print(np.trace(M))

#print(np.linalg.eigvals(M0))
#print(np.linalg.eigvals(M1))
#print(np.linalg.eigvals(Ma))

def getLambdas():
    lP = np.exp(-np.pi * 1j * alpha)
    lQ = np.exp(-np.pi * 1j * delta)
    lR = np.exp(-np.pi * 1j * epsilon)
    return lP,lQ,lR

def findTraces(M0, M1, Ma):
    """
    findTraces
    ===========================

    A simple helper function to find the required traces for our algorithm.

    Parameters:
    -----------
    Three matrices (as numpy arrays).

    Returns:
    ----------
    The traces of two pairwise products.
    """
    # lP, lQ, lR = getLambdas()
    t01 = np.trace(M0 * M1)/(np.sqrt(np.linalg.det(M0) * np.linalg.det(M1)))
    # print(np.linalg.det(M0) * np.linalg.det(M1))
    t1a = np.trace(M1 * Ma)/(np.sqrt(np.linalg.det(M1) * np.linalg.det(Ma)))
    # print(np.linalg.det(M1) * np.linalg.det(Ma))
    t0a = np.trace(M0 * Ma)/(np.sqrt(np.linalg.det(M0) * np.linalg.det(Ma)))
    # print(np.linalg.det(M0) * np.linalg.det(Ma))
    # print('-----MATRICES-----')
    # print(M0)
    # print(M1)
    # print(Ma)
    # t01 = np.trace(M0 * M1)/(lP * lQ)
    # t1a = np.trace(M1 * Ma)/(lQ * lR)
    # t0a = np.trace(M0 * Ma)/(lP * lR)
    return t01, t1a, t0a



#Tx.goto(100*x.real, 100*x.imag)
        #Ty.goto(25*y.real, 25*y.imag)
        #Tdy.goto(25*dy.real, 25*dy.imag)
        #Td2y.goto(5*d2y.real, 5*d2y.imag)
#print('Done')



def getNewEnergy(B):
    Mats = findMatrices(B)
    T0 = findTraces(Mats[0],Mats[1],Mats[2]) # [t12(B0), t23(B0)]
    return (T0[0].imag)**2 + (T0[1].imag)**2 + (T0[2].imag)**2

def getEnergyGradient(B,Bdelta = .0001):
    Mats = findMatrices(B)
    Mats1 = findMatrices(B + Bdelta)
    Tset0 = findTraces(Mats[0],Mats[1],Mats[2]) # [t12(B0), t23(B0)]
    Tset1 = findTraces(Mats1[0], Mats1[1], Mats1[2]) # [t12(B1), t23(B1)]
    dt12 = (Tset1[0] - Tset0[0])/(Bdelta)
    dt23 = (Tset1[1] - Tset0[1])/(Bdelta)
    dt13 = (Tset1[2] - Tset0[2])/(Bdelta)
    return 2 * (Tset0[0].imag * dt12.conjugate()*1j + Tset0[1].imag * dt23.conjugate()*1j + Tset0[2].imag * dt13.conjugate()*1j)



def newrunpass(passes = 20, Bdelta = .0001, setBstart = None, setSpeed = None, seta = None, setGamma = None, setEpsilon = None, setDelta = None, movement_min = None, B = B_init):
    global bees, speed, a, epsilon, delta
    if setBstart != None: # To allow external control of setting the B parameter
        B = setBstart
    if setSpeed != None: # To allow external control of setting the B parameter
        speed = setSpeed
    if setGamma != None:
        gamma = setGamma
    if seta != None:
        a = seta
    if setEpsilon != None:
        epsilon = setEpsilon
    if setDelta != None:
        delta = setDelta
    alpha = (gamma + delta + epsilon - 1) / 2
    beta = alpha
    bees.append([B.real, B.imag])

    B0 = B

    energy0 = getNewEnergy(B0)
    b_x = getEnergyGradient(B, Bdelta=Bdelta)
    
    ufactor = 0.1 * min(1,abs(1/b_x)) #* min(1,abs(b_x)/getNewEnergy(Tset0))
    B = B0 - b_x * ufactor

    energy1 = getNewEnergy(B)
    b_x2 = getEnergyGradient(B, Bdelta=Bdelta)


    #PARAMETERS FOR WOLFE CONDITION
    beta1 = 0.1 #
    beta2 = 0.9
    stepmult = 0.9
    count = 0
    while energy1 > energy0 -  abs(b_x) * abs(b_x) * ufactor * beta1 or abs((b_x2*b_x.conjugate()).real)/(abs(b_x)**2) > beta2:
        if energy1 > energy0 -  abs(b_x) * abs(b_x) * ufactor * beta1:
            count += 1
            print('COND1')
            ufactor = stepmult * ufactor
            B = B0 - b_x * ufactor
            energy1 = getNewEnergy(B)
            b_x2 = getEnergyGradient(B, Bdelta=Bdelta)
        else:
            count += 1
            print('COND2')
            ufactor = ufactor/stepmult
            B = B0 - b_x * ufactor
            energy1 = getNewEnergy(B)
            b_x2 = getEnergyGradient(B, Bdelta=Bdelta)
    print('WOLFE, step: ' + str(abs(b_x)* ufactor) + ', count: ' + str(count) + ', B: ' + str(B) + ', BX: ' + str(b_x) + ', Energy: ' + str(getNewEnergy(B)))
    
    if passes == 1:
        print('FINISHED' + str(B))
        return findMatrices(B),B
    elif passes ==  -1:
        if abs(b_x)*ufactor < speed/100:
            return findMatrices(B), B
        else:
            print('MAGS ' + str(abs(b_x)*ufactor) + ', ' + str(speed/100))
            return newrunpass(passes = passes, B = B)
    else:
        passes -= 1
        print('PASSES LEFT ' + str(passes))
        return newrunpass(passes = passes, B = B)
    


def runpass(passes = 20, Bdelta = .0001, setBstart = None, setSpeed = None, seta = None, setGamma = None, setEpsilon = None, setDelta = None, movement_min = None, B = B_init):
    '''
    Runpass
    ============================

    Recursively runs our descent algorithm to calculate possible accessory parameters.

    Parameters:
    -----------
    passes: The number of recursive calls
    Bdelta: The distance used to approximate the trace derivatives.
    setBstart: The initial value of B.
    setSpeed: Determines the speed of the monodromy calculations. Higher vs lower values are a trade off of speed vs time.
    seta: Used to set the third root a. Does not make a great difference in results.
    setEpsilon: Used to set the epsilon parameter in the Heun Equation. Default is 1/2
    setDelta: Used to set the delta parameter in the Heun Equation. Default is 1/2

    Returns:
    -----------
    The final value of B and its calculated monodromies.
    '''
    global bees, speed, a, epsilon, delta
    if setBstart != None: # To allow external control of setting the B parameter
        B = setBstart
    if setSpeed != None: # To allow external control of setting the B parameter
        speed = setSpeed
    if seta != None:
        a = seta
    if setGamma != None:
        gamma = setGamma
    if setEpsilon != None:
        epsilon = setEpsilon
    if setDelta != None:
        delta = setDelta
    alpha = (gamma + delta + epsilon - 1) / 2
    beta = alpha

    bees.append([B.real, B.imag])
    #print("Matrices")
    B0 = B
    B1 = B + Bdelta
    B = B0
    Mset0 = findMatrices(B)
    B = B1
    Mset1 = findMatrices(B)
    #print(str(Mset0[0]) + "\n" + str(Mset0[1]) + "\n" + str(Mset0[2]))
    #print(str(Mset1[0]) + "\n" + str(Mset1[1]) + "\n" + str(Mset1[2]))
    Tset0 = findTraces(Mset0[0],Mset0[1],Mset0[2]) # [t12(B0), t23(B0)]
    Tset1 = findTraces(Mset1[0], Mset1[1], Mset1[2]) # [t12(B1), t23(B1)]
    #print("Traces")
    #print(Tset1[1])
    #print(Tset0[1])
    dt12 = (Tset1[0] - Tset0[0])/(Bdelta)
    dt23 = (Tset1[1] - Tset0[1])/(Bdelta)
    lambdas = list(map(getLambda,Mset0))
    b_x = ((dt23/(lambdas[1]*lambdas[2])).conjugate()*((Tset0[0]/(lambdas[0]*lambdas[1])).imag) - (dt12/(lambdas[0]*lambdas[1])).conjugate()*((Tset0[1]/(lambdas[1]*lambdas[2])).imag))/((dt12.conjugate()*dt23/(lambdas[0].conjugate()*lambdas[1]*lambdas[1].conjugate()*lambdas[2])).imag)
    

    #print(dt12)
    #print(dt23)
    #print("X:")
    #print(b_x)

    ##############################################################
    # Change ufactor to reduce the convergence as much as needed #
    ##############################################################
    ufactor = 0.1 * min(1,1/abs(b_x))
    # if b_x > B0:
    #     ufactor = np.sqrt((B0)/b_x)
    B = B0 + b_x * ufactor
    #print(b_x)
    #print(B)
    #testMatrices(Mset0[0], Mset0[1], Mset0[2])
    if passes == 1:
        print('FINISHED' + str(B))
        return Mset0, B
    elif passes < 0:
        if abs(b_x) < setSpeed/100 or passes <= -300:
            return Mset0, B
        else:
            # print('MAGNITUDE: ' + str(abs(b_x)/(setSpeed/100)))
            passes -= 1
            return runpass(passes = passes, B = B)
    else:
        passes -= 1
        # print('PASSES LEFT' + str(passes))
        return runpass(passes = passes, B = B)




def makeEigenvalue(m, n):
    return 1.43554 * (complex(m,n) ** 2) + 0.114237 * complex(m,n) / complex(m,-n)

def getLambda(mat):
    det = np.linalg.det(mat)
    return cmath.sqrt(det)



#results = runpass()[0]
#print(results[0])
#print(results[1])
#print(results[2])
#print(B)
#print(findClosest(B))

#plt.plot(bees)
#plt.show()

#B^T\circxA * vec(X) = Vec (C)
#A = A*
#B = A
#C = X

#(A^T\circxA*)-I * vec(X) = 0
def complexToReal(mat):
    return np.array(
        [[mat[0:0].real, -mat[0:0].imag, mat[0:1].real, -mat[0:1].imag],
         [mat[0:0].imag, mat[0:0].real, mat[0:1].imag, mat[0:1].real],
         [mat[1:0].real, -mat[1:0].imag, mat[1:1].real, -mat[1:1].imag],
         [mat[1:0].imag, mat[1:0].real, mat[1:1].imag, -mat[1:1].real]])

def isHermit(mat, zero = 10**-10): # Does the matrix live in a small shack in the wilderness?
    return np.linalg.norm(mat - mat.transpose()) < zero

def constructErrorMat(basis):
    mat = []
    for m in basis:
        mat.append(np.reshape(m-m.transpose().conjugate(),(1,4)))

def solve(P,Q,R):
    x_basis = scipy.null_space(np.concatenate([np.kron(P.transpose(), P.transpose().conjugate())-np.identity(2),
                                               np.kron(Q.transpose(), Q.transpose().conjugate())-np.identity(2),
                                               np.kron(R.transpose(), R.transpose().conjugate())-np.identity(2)], axis=0), np.array([0]*12))
    out_basis = []
    for x in x_basis:
        if isHermit(complexToReal(np.reshape(x,2,2))):
            out_basis.append(x)

def testQuadTraces(P,Q,R):
    lambdaP = np.exp(np.pi * complex(0, 1) * (1 - gamma))
    lambdaQ = np.exp(np.pi * complex(0, 1) * (1 - delta))
    lambdaR = np.exp(np.pi * complex(0, 1) * (1 - epsilon))
    P0 = P/lambdaP
    Q0 = Q/lambdaQ
    R0 = R/lambdaR

    p = np.trace(P0)
    q = np.trace(Q0)
    r = np.trace(R0)
    tau = np.trace(P0*Q0)
    sigma = np.trace(P0*R0)
    rho = np.trace(Q0*R0)

    a = tau**2 + q**2 + p**2 - 2 * p * tau * q - 4
    b = sigma**2 + r**2 + p**2 - 2 * p * sigma * r - 4
    c = P0[0,1] * R0[1,0] + P0[1,0] * R0[0,1]

    if a >= 0 and b >= 0 and (c**2-4*a*b) <= 0:
        return True
    else:
        return False

    #return a, b, (c**2-4*a*b)
def testrunpass(setBstart = None, setSpeed = None, seta = None, setEpsilon = None, setDelta = None, movement_min = None):
    global B, bees, speed, a, epsilon, delta
    if setBstart != None: # To allow external control of setting the B parameter
        B = setBstart
    if setSpeed != None: # To allow external control of setting the B parameter
        speed = setSpeed
    if seta != None:
        a = seta
    if setEpsilon != None:
        epsilon = setEpsilon
    if setDelta != None:
        delta = setDelta
    alpha = (gamma + delta + epsilon - 1) / 2
    beta = alpha
    Mset = findMatrices(B)
    return testQuadTraces(Mset[0],Mset[1],Mset[2])
    
def asymptotics(m, n):
    m_1 = 1/4
    m_2 = 1/4
    m_3 = 7/16

def testMatrices(P,Q,R):
    print(str(P) + ' ' + str(Q) + ' ' + str(R))
    #print(np.trace(P) + ' ' + np.trace(Q) + ' ' + np.trace(R))


#####   Testing   #####

# MSet,B = newrunpass(passes=-1, setBstart= 3, setSpeed=0.001, setAlpha = 0.5, setEpsilon = 0.125, setDelta=0.50)
# print(MSet)
# print(B)