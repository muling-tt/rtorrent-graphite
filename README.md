# rtorrent-graphite
Get rTorrent stats via XML-RPC and push to graphite (carbon). Depends on [graphitesend](https://github.com/daniellawrence/graphitesend)

####Currently supported metrics are:

* Total bandwidth used up/down
* Maximum set bandwidth up/down
* Total memory used
* Maximum set memory
* Total number of torrents loaded
* Number of complete torrents
* Number of incomplete torrents
* Bytes remaining/done
* Total number of peers/seeds/accounted

Blog post: https://muling.lu/rtorrent-graphite
