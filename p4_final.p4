/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;   //转发端口号定义
typedef bit<48> macAddr_t;      //48位MAC地址定义
typedef bit<32> ip4Addr_t;      //32位ipv4地址定义

header ethernet_t {
    macAddr_t dstAddr;          //目的MAC
    macAddr_t srcAddr;          //源MAC
    bit<16>   etherType;        //数据字段协议
}           //以太网协议


header ipv4_t {                 //根据论文中的内容，定义IP数据包头
    bit<4>    version;          //版本
    bit<4>    ihl;              //首部长度
    bit<8>    diffserv;         //区分服务
    bit<16>   totalLen;         //总长度
    bit<16>   identification;   //标识
    bit<3>    flags;            //标志
    bit<13>   fragOffset;       //片偏移
    bit<8>    ttl;              //生存时间
    bit<8>    protocol;         //协议
    bit<16>   hdrChecksum;      //首部检验和
    ip4Addr_t srcAddr;          //源地址
    ip4Addr_t dstAddr;          //目的地址
}           //IPv4协议

struct metadata {
    /* empty */
}           //元数据

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
}           //将以太网和ipv4协议的数据放入头部

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,                   //当前传入或等待处理的包
                out headers hdr,                    //out类型的包头
                inout metadata meta,                //p4执行过程中的中间数据
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_eth;                       //使用parse_ethernet使parser在状态之间转换
    }

    state parse_eth {
        packet.extract(hdr.ethernet);               //提取头部中的以太网内容
        transition select(hdr.ethernet.etherType) { //根据头部中的内容选择不同的状态
            TYPE_IPV4: parse_ipv4;
            default: accept;                        //如果不是ipv4，则直接跳过解析
        }
    }

    //根据论文中的内容，定义解析器及其包头提取
    state parse_ipv4 {                              //自定义的ipv4状态
        packet.extract(hdr.ipv4);                   //提取头部中的ipv4
        transition accept;                          //提取完毕，解析完毕
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}           //校验和验证


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
action drop() {
        mark_to_drop();                                 //丢弃包
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;           //配置下一跳的接口
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;                 //将以太网源地址更新为交换机地址
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;                //TTL衰减
    }

    //根据论文的内容，定义三个匹配+动作表
    table ipv4_lpm {                        //定义匹配表，用于查询使用的匹配方式，一般有exact、ternary、lpm三种匹配方式
        key = {
            hdr.ipv4.dstAddr: lpm;          //若头部ipv4部分中的目的地址是ipm，则运行actions
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;                        //一个指定的所需的表大小的整数
        default_action = NoAction();        //当查询表中的查询无法找到匹配的key值时
    }

    table ipv4_lpm2 {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }

    table ipv4_lpm3 {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    
    //根据论文的内容，根据TOS字段的内容选择一个匹配+动作表并应用
        apply {
        if (hdr.ipv4.isValid()) {                   //当ipv4头部有效时
            if(hdr.ipv4.diffserv == 0) {
                ipv4_lpm.apply();
            }
            else if(hdr.ipv4.diffserv == 4) {
                ipv4_lpm2.apply();
            }
            else {
                ipv4_lpm3.apply();
            }
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }               //校验和计算
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
    }               //选择头部中的以太网和ipv4字段放入传出数据包中
}                   //反解析

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;