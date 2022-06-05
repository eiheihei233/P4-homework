#!/usr/bin/env python3
import argparse
import os
import sys
from time import sleep

import grpc

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 './utils/'))
import p4runtime_lib.bmv2
import p4runtime_lib.helper
from p4runtime_lib.error_utils import printGrpcError
from p4runtime_lib.switch import ShutdownAllSwitchConnections

def LpmRulesWriting(p4info_helper, ingress_sw,
                        match_fields, dstAddr, port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm",
        match_fields={
            "hdr.ipv4.dstAddr": match_fields
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dstAddr,
            "port": port
        }
    )
    ingress_sw.WriteTableEntry(table_entry)
def Lpm2RulesWriting(p4info_helper, ingress_sw,
                        match_fields, dstAddr, port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm2",
        match_fields={
            "hdr.ipv4.dstAddr": match_fields
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dstAddr,
            "port": port
        }
    )
    ingress_sw.WriteTableEntry(table_entry)
def Lpm3RulesWriting(p4info_helper, ingress_sw,
                        match_fields, dstAddr, port):
    table_entry = p4info_helper.buildTableEntry(
        table_name="MyIngress.ipv4_lpm3",
        match_fields={
            "hdr.ipv4.dstAddr": match_fields
        },
        action_name="MyIngress.ipv4_forward",
        action_params={
            "dstAddr": dstAddr,
            "port": port
        }
    )
    ingress_sw.WriteTableEntry(table_entry)

def main(p4info_file_path, bmv2_file_path):
    p4info_helper = p4runtime_lib.helper.P4InfoHelper(p4info_file_path)
    #初始化s1-s6
    try:
        s1 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s1',
            address='127.0.0.1:50051',
            device_id=0,
            proto_dump_file='logs/s1-p4runtime-requests.txt')
        s2 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s2',
            address='127.0.0.1:50052',
            device_id=1,
            proto_dump_file='logs/s2-p4runtime-requests.txt')
        s3 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s3',
            address='127.0.0.1:50053',
            device_id=2,
            proto_dump_file='logs/s3-p4runtime-requests.txt')
        s4 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s4',
            address='127.0.0.1:50054',
            device_id=3,
            proto_dump_file='logs/s4-p4runtime-requests.txt')
        s5 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s5',
            address='127.0.0.1:50055',
            device_id=4,
            proto_dump_file='logs/s5-p4runtime-requests.txt')
        s6 = p4runtime_lib.bmv2.Bmv2SwitchConnection(
            name='s6',
            address='127.0.0.1:50056',
            device_id=5,
            proto_dump_file='logs/s6-p4runtime-requests.txt')
        
        #进行s1-s6的MasterArbitration设置
        s1.MasterArbitrationUpdate()
        s2.MasterArbitrationUpdate()
        s3.MasterArbitrationUpdate()
        s4.MasterArbitrationUpdate()
        s5.MasterArbitrationUpdate()
        s6.MasterArbitrationUpdate()
        
        #进行s1-s6的ForwardingPipelineConfig设置
        s1.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        s2.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s2")
        s3.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s3")
        s4.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s4")
        s5.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s5")
        s6.SetForwardingPipelineConfig(p4info=p4info_helper.p4info,
                                       bmv2_json_file_path=bmv2_file_path)
        print("Installed P4 Program using SetForwardingPipelineConfig on s6")
        
        # s1的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s1, ["10.0.1.1", 32], "00:00:00:00:01:11", 1)
        LpmRulesWriting(p4info_helper, s1, ["10.0.2.2", 32], "00:00:00:00:02:04", 2)
        LpmRulesWriting(p4info_helper, s1, ["10.0.3.3", 32], "00:00:00:00:03:02", 3)
        LpmRulesWriting(p4info_helper, s1, ["10.0.4.4", 32], "00:00:00:00:02:04", 2)
        LpmRulesWriting(p4info_helper, s1, ["10.0.5.5", 32], "00:00:00:00:02:04", 2)
        LpmRulesWriting(p4info_helper, s1, ["10.0.6.6", 32], "00:00:00:00:03:02", 3)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.1.1", 32], "00:00:00:00:01:11", 1)
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.2.2", 32], "00:00:00:00:02:04", 2)
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.3.3", 32], "00:00:00:00:03:02", 3)
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.4.4", 32], "00:00:00:00:03:02", 3)
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.5.5", 32], "00:00:00:00:03:02", 3)
        Lpm2RulesWriting(p4info_helper, s1, ["10.0.6.6", 32], "00:00:00:00:03:02", 3)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.1.1", 32], "00:00:00:00:01:11", 1)
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.2.2", 32], "00:00:00:00:02:04", 2)
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.3.3", 32], "00:00:00:00:03:02", 3)
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.4.4", 32], "00:00:00:00:02:04", 2)
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.5.5", 32], "00:00:00:00:02:04", 2)
        Lpm3RulesWriting(p4info_helper, s1, ["10.0.6.6", 32], "00:00:00:00:02:04", 2)

        # s2的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s2, ["10.0.1.1", 32], "00:00:00:00:01:02", 4)
        LpmRulesWriting(p4info_helper, s2, ["10.0.2.2", 32], "00:00:00:00:02:22", 1)
        LpmRulesWriting(p4info_helper, s2, ["10.0.3.3", 32], "00:00:00:00:03:03", 3)
        LpmRulesWriting(p4info_helper, s2, ["10.0.4.4", 32], "00:00:00:00:05:04", 2)
        LpmRulesWriting(p4info_helper, s2, ["10.0.5.5", 32], "00:00:00:00:05:04", 2)
        LpmRulesWriting(p4info_helper, s2, ["10.0.6.6", 32], "00:00:00:00:03:03", 3)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.1.1", 32], "00:00:00:00:01:02", 4)
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.2.2", 32], "00:00:00:00:02:22", 1)
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.3.3", 32], "00:00:00:00:03:03", 3)
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.4.4", 32], "00:00:00:00:03:03", 3)
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.5.5", 32], "00:00:00:00:03:03", 3)
        Lpm2RulesWriting(p4info_helper, s2, ["10.0.6.6", 32], "00:00:00:00:03:03", 3)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.1.1", 32], "00:00:00:00:01:02", 4)
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.2.2", 32], "00:00:00:00:02:22", 1)
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.3.3", 32], "00:00:00:00:01:02", 4)
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.4.4", 32], "00:00:00:00:05:04", 2)
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.5.5", 32], "00:00:00:00:05:04", 2)
        Lpm3RulesWriting(p4info_helper, s2, ["10.0.6.6", 32], "00:00:00:00:05:04", 2)

        # s3的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s3, ["10.0.1.1", 32], "00:00:00:00:01:03", 2)
        LpmRulesWriting(p4info_helper, s3, ["10.0.2.2", 32], "00:00:00:00:02:03", 3)
        LpmRulesWriting(p4info_helper, s3, ["10.0.3.3", 32], "00:00:00:00:03:33", 1)
        LpmRulesWriting(p4info_helper, s3, ["10.0.4.4", 32], "00:00:00:00:06:02", 4)
        LpmRulesWriting(p4info_helper, s3, ["10.0.5.5", 32], "00:00:00:00:02:03", 3)
        LpmRulesWriting(p4info_helper, s3, ["10.0.6.6", 32], "00:00:00:00:06:02", 4)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.1.1", 32], "00:00:00:00:01:03", 2)
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.2.2", 32], "00:00:00:00:02:03", 3)
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.3.3", 32], "00:00:00:00:03:33", 1)
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.4.4", 32], "00:00:00:00:06:02", 4)
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.5.5", 32], "00:00:00:00:06:02", 4)
        Lpm2RulesWriting(p4info_helper, s3, ["10.0.6.6", 32], "00:00:00:00:06:02", 4)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.1.1", 32], "00:00:00:00:01:03", 2)
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.2.2", 32], "00:00:00:00:01:03", 2)
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.3.3", 32], "00:00:00:00:03:33", 1)
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.4.4", 32], "00:00:00:00:06:02", 4)
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.5.5", 32], "00:00:00:00:06:02", 4)
        Lpm3RulesWriting(p4info_helper, s3, ["10.0.6.6", 32], "00:00:00:00:06:02", 4)
        

        # s4的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s4, ["10.0.1.1", 32], "00:00:00:00:06:04", 2)
        LpmRulesWriting(p4info_helper, s4, ["10.0.2.2", 32], "00:00:00:00:05:02", 3)
        LpmRulesWriting(p4info_helper, s4, ["10.0.3.3", 32], "00:00:00:00:06:04", 2)
        LpmRulesWriting(p4info_helper, s4, ["10.0.4.4", 32], "00:00:00:00:04:44", 1)
        LpmRulesWriting(p4info_helper, s4, ["10.0.5.5", 32], "00:00:00:00:05:02", 3)
        LpmRulesWriting(p4info_helper, s4, ["10.0.6.6", 32], "00:00:00:00:06:04", 2)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.1.1", 32], "00:00:00:00:06:04", 2)
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.2.2", 32], "00:00:00:00:06:04", 2)
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.3.3", 32], "00:00:00:00:06:04", 2)
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.4.4", 32], "00:00:00:00:04:44", 1)
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.5.5", 32], "00:00:00:00:05:02", 3)
        Lpm2RulesWriting(p4info_helper, s4, ["10.0.6.6", 32], "00:00:00:00:06:04", 2)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.1.1", 32], "00:00:00:00:06:04", 2)
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.2.2", 32], "00:00:00:00:05:02", 3)
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.3.3", 32], "00:00:00:00:06:04", 2)
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.4.4", 32], "00:00:00:00:04:44", 1)
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.5.5", 32], "00:00:00:00:05:02", 3)
        Lpm3RulesWriting(p4info_helper, s4, ["10.0.6.6", 32], "00:00:00:00:06:04", 2)

        # s5的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s5, ["10.0.1.1", 32], "00:00:00:00:02:02", 4)
        LpmRulesWriting(p4info_helper, s5, ["10.0.2.2", 32], "00:00:00:00:02:02", 4)
        LpmRulesWriting(p4info_helper, s5, ["10.0.3.3", 32], "00:00:00:00:06:03", 3)
        LpmRulesWriting(p4info_helper, s5, ["10.0.4.4", 32], "00:00:00:00:04:03", 2)
        LpmRulesWriting(p4info_helper, s5, ["10.0.5.5", 32], "00:00:00:00:05:55", 1)
        LpmRulesWriting(p4info_helper, s5, ["10.0.6.6", 32], "00:00:00:00:06:03", 3)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.1.1", 32], "00:00:00:00:06:03", 3)
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.2.2", 32], "00:00:00:00:06:03", 3)
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.3.3", 32], "00:00:00:00:06:03", 3)
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.4.4", 32], "00:00:00:00:04:03", 2)
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.5.5", 32], "00:00:00:00:05:55", 1)
        Lpm2RulesWriting(p4info_helper, s5, ["10.0.6.6", 32], "00:00:00:00:06:03", 3)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.1.1", 32], "00:00:00:00:02:02", 4)
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.2.2", 32], "00:00:00:00:02:02", 4)
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.3.3", 32], "00:00:00:00:06:03", 3)
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.4.4", 32], "00:00:00:00:04:03", 2)
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.5.5", 32], "00:00:00:00:05:55", 1)
        Lpm3RulesWriting(p4info_helper, s5, ["10.0.6.6", 32], "00:00:00:00:06:03", 3)
        

        # s6的流规则下发
        ## lpm
        LpmRulesWriting(p4info_helper, s6, ["10.0.1.1", 32], "00:00:00:00:03:04", 2)
        LpmRulesWriting(p4info_helper, s6, ["10.0.2.2", 32], "00:00:00:00:05:03", 3)
        LpmRulesWriting(p4info_helper, s6, ["10.0.3.3", 32], "00:00:00:00:03:04", 2)
        LpmRulesWriting(p4info_helper, s6, ["10.0.4.4", 32], "00:00:00:00:04:02", 4)
        LpmRulesWriting(p4info_helper, s6, ["10.0.5.5", 32], "00:00:00:00:05:03", 3)
        LpmRulesWriting(p4info_helper, s6, ["10.0.6.6", 32], "00:00:00:00:06:66", 1)
        ## lpm2
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.1.1", 32], "00:00:00:00:03:04", 2)
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.2.2", 32], "00:00:00:00:03:04", 2)
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.3.3", 32], "00:00:00:00:03:04", 2)
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.4.4", 32], "00:00:00:00:04:02", 4)
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.5.5", 32], "00:00:00:00:05:03", 3)
        Lpm2RulesWriting(p4info_helper, s6, ["10.0.6.6", 32], "00:00:00:00:06:66", 1)
        ## lpm3
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.1.1", 32], "00:00:00:00:03:04", 2)
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.2.2", 32], "00:00:00:00:05:03", 3)
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.3.3", 32], "00:00:00:00:03:04", 2)
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.4.4", 32], "00:00:00:00:04:02", 4)
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.5.5", 32], "00:00:00:00:05:03", 3)
        Lpm3RulesWriting(p4info_helper, s6, ["10.0.6.6", 32], "00:00:00:00:06:66", 1)




     
    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='P4Runtime Controller')
    parser.add_argument('--p4info', help='p4info proto in text format from p4c',
                        type=str, action="store", required=False,
                        default='./build/p4-final.p4.p4info.txt')
    parser.add_argument('--bmv2-json', help='BMv2 JSON file from p4c',
                        type=str, action="store", required=False,
                        default='./build/p4-final.json')
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file not found: %s\nHave you run 'make'?" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file not found: %s\nHave you run 'make'?" % args.bmv2_json)
        parser.exit(1)
    main(args.p4info, args.bmv2_json)