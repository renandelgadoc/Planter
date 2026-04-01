# THIS FILE IS PART OF Planter PROJECT
# Planter.py - The core part of the Planter library
#
# THIS PROGRAM IS FREE SOFTWARE TOOL, WHICH MAPS MACHINE LEARNING ALGORITHMS TO DATA PLANE, IS LICENSED UNDER Apache-2.0
# YOU SHOULD HAVE RECEIVED A COPY OF THE LICENSE, IF NOT, PLEASE CONTACT THE FOLLOWING E-MAIL ADDRESSES
#
# Copyright (c) 2020-2021 Changgang Zheng
# Copyright (c) Computing Infrastructure Lab, Department of Engineering Science, University of Oxford
# E-mail: changgang.zheng@eng.ox.ac.uk or changgangzheng@qq.com
#
# Functions: This file is a use case-related P4 generator (router with Planter ML support).
#            Combines router functionality with Planter machine learning capabilities.
#            Please refer to ./Docs/Planter_User_Document.pdf or further information.

import numpy as np

def common_basic_headers(fname, config):
    with open(fname, 'a') as headers:

        headers.write("const bit<16> TYPE_IPV4 = 0x0800;\n"
                      "const bit<8> IP_PROTO_ICMP = 1;\n"
                      "const bit<16> ETHERTYPE_Planter = 0x1234;\n"
                      "const bit<8>  Planter_P     = 0x50;   // 'P'\n"
                      "const bit<8>  Planter_4     = 0x34;   // '4'\n"
                      "const bit<8>  Planter_VER   = 0x01;   // v0.1\n\n")

        headers.write("header ethernet_t {\n"
                      "    bit<48> dstAddr;\n"
                      "    bit<48> srcAddr;\n"
                      "    bit<16> etherType;\n"
                      "}\n\n")

        headers.write("header ipv4_t {\n"
                      "    bit<4>   version;\n"
                      "    bit<4>   ihl;\n"
                      "    bit<8>   diffserv;\n"
                      "    bit<16>  totalLen;\n"
                      "    bit<16>  identification;\n"
                      "    bit<3>   flags;\n"
                      "    bit<13>  fragOffset;\n"
                      "    bit<8>   ttl;\n"
                      "    bit<8>   protocol;\n"
                      "    bit<16>  hdrChecksum;\n"
                      "    bit<32>  srcAddr;\n"
                      "    bit<32>  dstAddr;\n"
                      "}\n\n")

def common_metadata(fname, config):
    with open(fname, 'a') as headers:
        headers.write("    bit<1> is_my_mac;\n")
        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> result;\n")
        headers.write("    bit<8> flag ;\n")

def common_headers(fname, config):
    with open(fname, 'a') as headers:
        # write Planter header
        headers.write("header Planter_h {\n"
                      "    bit<8> p;\n"
                      "    bit<8> four;\n"
                      "    bit<8> ver;\n"
                      "    bit<8> typ;\n")

        for f in range(0, config['num_features']):
            headers.write("    bit<32> feature" + str(f) + ";\n")
        headers.write("    bit<32> result;\n")
        headers.write("}\n\n")

        # write the headers' structure
        headers.write("struct header_t {\n"
                      "    ethernet_t   ethernet;\n"
                      "    ipv4_t       ipv4;\n"
                      "    Planter_h    Planter;\n"
                      "}\n\n")

def common_parser(fname, config):
    with open(fname, 'a') as parser:
        parser.write("    state parse_ethernet {\n"
                     "        pkt.extract(hdr.ethernet);\n"
                     "        transition select(hdr.ethernet.etherType) {\n"
                     "            TYPE_IPV4      : parse_ipv4;\n"
                     "            ETHERTYPE_Planter : check_planter_version;\n"
                     "            default        : accept;\n"
                     "        }\n"
                     "    }\n\n"
                     "    state parse_ipv4 {\n"
                     "        pkt.extract(hdr.ipv4);\n"
                     "        transition accept;\n"
                     "    }\n\n"
                     "    state check_planter_version {\n"
                     "        transition select(pkt.lookahead<Planter_h>().p,\n"
                     "                          pkt.lookahead<Planter_h>().four,\n"
                     "                          pkt.lookahead<Planter_h>().ver) {\n"
                     "            (Planter_P, Planter_4, Planter_VER) : parse_planter;\n"
                     "            default                             : accept;\n"
                     "        }\n"
                     "    }\n\n"
                     "    state parse_planter {\n"
                     "        pkt.extract(hdr.Planter);\n")
        for f in range(0, config['num_features']):
            parser.write("        meta.feature" + str(f) + " = hdr.Planter.feature" + str(f) + ";\n")
        parser.write("        meta.flag = 1;\n")
        parser.write("        transition accept;\n"
                     "    }\n")

def common_tables(fname, config):
    with open(fname, 'a') as ingress:
        # Router actions
        ingress.write("    action mark_as_my_mac() {\n"
                      "        meta.is_my_mac = 1;\n"
                      "    }\n\n"
                      "    action set_nhop(bit<48> dst_mac, bit<48> src_mac, bit<9> port) {\n"
                      "        hdr.ethernet.dstAddr = dst_mac;\n"
                      "        hdr.ethernet.srcAddr = src_mac;\n"
                      "        ig_intr_md.egress_spec = port;\n"
                      "        if (hdr.ipv4.isValid() && hdr.ipv4.ttl > 0) {\n"
                      "            hdr.ipv4.ttl = hdr.ipv4.ttl - 1;\n"
                      "        }\n"
                      "    }\n\n")

        # Router tables
        ingress.write("    table my_mac {\n"
                      "        key = {\n"
                      "            hdr.ethernet.dstAddr : exact;\n"
                      "        }\n"
                      "        actions = {\n"
                      "            mark_as_my_mac;\n"
                      "            drop;\n"
                      "        }\n"
                      "        size = 8;\n"
                      "        default_action = drop();\n"
                      "    }\n\n"
                      "    table ipv4_lpm {\n"
                      "        key = {\n"
                      "            hdr.ipv4.dstAddr: lpm;\n"
                      "        }\n"
                      "        actions = {\n"
                      "            set_nhop;\n"
                      "            drop;\n"
                      "        }\n"
                      "        size = 1024;\n"
                      "        default_action = drop();\n"
                      "    }\n\n")

def common_logics(fname, config):
    with open(fname, 'a') as ingress:
        ingress.write("        meta.is_my_mac = 0;\n"
                      "        my_mac.apply();\n\n"
                      "        if (meta.is_my_mac == 0) {\n"
                      "            drop();\n"
                      "            return;\n"
                      "        }\n\n"
                      "        if (hdr.ipv4.isValid() && hdr.ipv4.protocol == IP_PROTO_ICMP) {\n"
                      "            log_msg(\"ICMP ping received\");\n"
                      "        }\n\n"
                      "        if (hdr.ipv4.isValid()) {\n"
                      "            if (hdr.ipv4.ttl <= 1) {\n"
                      "                drop();\n"
                      "            } else {\n"
                      "                ipv4_lpm.apply();\n"
                      "            }\n"
                      "        }\n\n"
                      "        // ML classification logic will be inserted here\n")

def common_compute_checksum(parser, config):
        parser.write("    apply {\n"
                      "        update_checksum(\n"
                      "            hdr.ipv4.isValid(),\n"
                      "            { hdr.ipv4.version,\n"
                      "              hdr.ipv4.ihl,\n"
                      "              hdr.ipv4.diffserv,\n"
                      "              hdr.ipv4.totalLen,\n"
                      "              hdr.ipv4.identification,\n"
                      "              hdr.ipv4.flags,\n"
                      "              hdr.ipv4.fragOffset,\n"
                      "              hdr.ipv4.ttl,\n"
                      "              hdr.ipv4.protocol,\n"
                      "              hdr.ipv4.srcAddr,\n"
                      "              hdr.ipv4.dstAddr },\n"
                      "            hdr.ipv4.hdrChecksum,\n"
                      "            HashAlgorithm.csum16\n"
                      "        );\n"
                      "    }\n")

def common_deparser(fname, config):
    with open(fname, 'a') as deparser:
        deparser.write("    apply {\n"
                       "        pkt.emit(hdr.ethernet);\n"
                       "        pkt.emit(hdr.ipv4);\n"
                       "        pkt.emit(hdr.Planter);\n"
                       "    }\n")
