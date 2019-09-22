Siraj Hassan

How to run: (made with Python3)

1) To run metaData server input on one terminal: 'python3 metaServer.py'

2) To run multiple peer server, open on each terminal and run: 'python3 peer.py'

3) When starting peer:
      Enter 1, since I did not finish phase 2.
      Enter id
      Enter topo or press Enter
      Enter flag 'p2p'


Methodology:
  My p2p network has a threaded metaData server that will accept connections
  from peers continiously. The MetaData Server is threaded so
  that is can handle many requests at a time, and can start running again if there is
  a problem with a peer.

    If it is the first peer in the network, the metaServer will notify
  the new peer log its information in the cache (id,ip,port),
   and the new peer will disconnect. The MetaData Server is threaded so
  that is can handle many requests at a time, and can start running again if there is
   a problem with a peer.

    For other peers that are not first, it sends its entire topology of the
  p2p network to the new peer. Then the new peer will search through that cache's
  information one by one, from top to bottom..

    The new peer open a temporary socket will ping peers in the cache from
  top to bottom until a peer with an open port is found. Then, the new peer
  will notify the MetaServer it is no longer needed, and will close the socket
  with the metaServer.

    Afterward, the new peer will join the p2p network at the
  port it found. The peer has two sockets. A connection socket, which it uses
  to join the p2p network, and a listening socket, which other peers can join the
  network with. Also information is sent to and from both sockets.

  Notes/assumptions:
   -   Topology is shown in the form [ID, IP , PORT]
   -  'topo' will make the neighbors on each peer show up on the terminal
   -   I did not have phase 2 done in my project.
   -   I could not get a proper 'Stop' function to work on Mac OS.
   -   So, I did not include it. Please press ^C.
