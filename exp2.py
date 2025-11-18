from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, DefaultController
from mininet.cli import CLI
from mininet.log import setLogLevel

class Exp2Topo(Topo):

    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Add hosts
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')

        # Add switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add links based on the topology diagram
        # h1 connects to s1 via h1-eth0 and s1-eth1
        self.addLink(h1, s1)
        
        # h2 connects to s1 via h2-eth0 and s1-eth2
        self.addLink(h2, s1)
        
        # s1 connects to s2 via s1-eth3 and s2-eth1
        self.addLink(s1, s2)
        
        # h3 connects to s2 via h3-eth0 and s2-eth2
        self.addLink(h3, s2)

def main():
    topo = Exp2Topo()
    setLogLevel('info')
    
    # Create network with OVSKernelSwitch and DefaultController
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        controller=DefaultController,
        autoSetMacs=True
    )
    
    net.start()
    
    # Start CLI for user interaction
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    main()
