# ExpressVPN
Docker container for working with ExpressVPN.
I recommend putting this container with others to act as the outgoing container. Containers should use this container as its network (this will ensure the other container won't "leak") and publish all ports you need for the containers attached at the VPN container. Additionally, ExpressVPN seems to randomly disconnect long-standing connections. To combat this, the container attempts to re-establish the connection and completely restarts the container if it is unable to do so.

The restart does the trick but most containers attached to it will lose all network. My recommendation is that your container orchestrator restart the connected containers after this container becomes healthy again to restore connectivity.

# Instructions
- Pull image from Docker as dietolead/ExpressVPN
- Login to your ExpressVPN account and acquire your activation code
- A Docker swarm/compose or a Kubernetes cluster is recommended, but not required
- Ports exposed should be at the VPN container, not at the container that will be listening

Example docker run command:
```
docker run -d --privileged -env ACTIVATION=(activation code) \
    -env LOCATION=(valid CLI ExpressVPN location) --device=/dev/net/tun \
    --restart=unless-stopped --cap-add=NET_ADMIN \
    -p (ports the other containers need) dietolead/ExpressVPN
```