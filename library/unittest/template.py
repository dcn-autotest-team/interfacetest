#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# *********************************************************************
# Software : PyCharm
#
# template.py - 
#
# Author    :yanwh(yanwh@digitalchina.com)
#
# Version 1.0.0
#
# Copyright (c) 2004-9999 Digital China Networks Co. Ltd 
#
#
# *********************************************************************
# Change log:
#       - 2018/10/13 14:35  add by yanwh
#
# *********************************************************************


class Template_mixin:
    STATUS = {
        0: 'Pass',
        1: 'Fail',
        2: 'Error',
        3: 'Skip',
    }

    DEFAULT_DESCRIPTION = ''

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<!DOCTYPE html>
<html lang="zh-cn">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <title>%(title)s</title>
    <meta name="generator" content="%(generator)s"/>
    <link rel="stylesheet" href="http://cdn.bootcss.com/bootstrap/3.3.0/css/bootstrap.min.css">
    %(stylesheet)s

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
<body>
<script language="javascript" type="text/javascript"><!--
output_list = Array();

/* level - 0:Summary; 1:Failed; 2:Skip; 3:All */
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;


        if (id.substr(0, 2) === 'ft') {
            if (level === 1 || level === 3) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
        if (id.substr(0, 2) === 'pt') {
            if (level === 3) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
        if (id.substr(0, 2) === 'st') {
            if (level === 2 || level === 3) {
                tr.className = '';
            }
            else {
                tr.className = 'hiddenRow';
            }
        }
    }
}

function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;
    for (var i = 0; i < count; i++) {
        tid0 = 't' + cid.substr(1) + '.' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'p' + tid0;
            tr = document.getElementById(tid);
        }
        if (!tr) {
            tid = 's' + tid0;
            tr = document.getElementById(tid);
        }
        id_list[i] = tid;
        if (tr.className) {
            toHide = 0;
        }
    }
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        if (toHide) {
            if(document.getElementById('div_'+tid)){
                document.getElementById('div_'+tid).style.display = 'none'
            }            
            document.getElementById(tid).className = 'hiddenRow';
        }
        else {
            document.getElementById(tid).className = '';
        }
    }
}


function showTestDetail(div_id){
    var details_div = document.getElementById(div_id)
    var displayState = details_div.style.display
    // alert(displayState)
    if (displayState != 'block' ) {
        displayState = 'block'
        details_div.style.display = 'block'
    }
    else {
        details_div.style.display = 'none'
    }
}


function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}

/* obsoleted by detail in <div>
function showOutput(id, name) {
    var w = window.open("", //url
                    name,
                    "resizable,scrollbars,status,width=800,height=450");
    d = w.document;
    d.write("<pre>");
    d.write(html_escape(output_list[id]));
    d.write("\n");
    d.write("<a href='javascript:window.close()'>close</a>\n");
    d.write("</pre>\n");
    d.close();
}
*/
--></script>

<div class="main_container">
    %(heading)s

    %(report)s
</div>
</body>
</html>
"""
    # variables: (title, generator, stylesheet, heading, report, ending)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">

.btn-sg-pass {
  color: #333; 
  background-color: #fff;
  border-color: #ccc;
  font-size: 15px;
}

.btn-sg-fail {
  color: #fff;
  background-color: #d9534f;
  border-color: #ccc;
  font-size: 15px;
}

.main_container{
    width: 1500px;
    padding-right: 15px;
    padding-left: 15px;
    margin-right: auto;
    margin-left: auto;
}

/* -- css div popup ------------------------------------------------------------------------ */
.popup_window {
    display: none;
    position: relative;
    left: 0px;
    top: 0px;
    /*border: solid #627173 1px; */
    padding: 10px;
    background-color: #99CCFF;
    font-family: "Microsoft YaHei","Lucida Console", "Courier New", Courier, monospace;
    text-align: left;
    font-size: 10pt;
    width: 800px;
}

/* -- report ------------------------------------------------------------------------ */

#show_detail_line .label {
    font-size: 85%;
    cursor: pointer;
}

#show_detail_line {
    margin: 2em auto 1em auto;
}

#total_row  { font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em; }

</style>
"""

    HEADING_TMPL = """<div class='heading head_container'>
<h2>%(title)s</h2>
%(parameters)s
<p class='description'>%(description)s</p>


"""  # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p><strong>%(name)s:</strong> %(value)s</p>
"""
    REPORT_TMPL = """

    <p id='show_detail_line'>
    <span class="label label-primary" onclick="showCase(0)">Summary</span>
    <span class="label label-danger" onclick="showCase(1)">Failed</span>
    <span class="label label-info" onclick="showCase(2)">Skip</span>
    <span class="label label-default" onclick="showCase(3)">All</span>
    </p>
</div>
<div>
<table id='result_table' class="table">
    <thead>
        <tr id='header_row'>
            <th>Test Group/Test case</td>
            <th>Count</td>
            <th>Pass</td>
            <th>Fail</td>
            <th>Error</td>
            <th>Skip</td>
            <th>View</td>
        </tr>
    </thead>
    <tbody>
        %(test_list)s
    </tbody>
    <tfoot>
        <tr id='total_row'>
            <td>Total</td>
            <td>%(count)s</td>
            <td class="text text-success">%(Pass)s</td>
            <td class="text text-danger">%(fail)s</td>
            <td class="text text-warning">%(error)s</td>
            <td class="text text-warning">%(skip)s</td>
            <td>&nbsp;</td>
        </tr>
    </tfoot>
</table>
</div>
"""

    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s'>
    <td>%(desc)s</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>%(skip)s</td>
    <td><a class="btn btn-xs btn-primary"href="javascript:showClassDetail('%(cid)s',%(count)s)">Detail</a></td>
</tr>
"""  # variables: (style, desc, count, Pass, fail, error, cid)

    REPORT_TEST_WITH_OUTPUT_TMPL_PASS = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>

    <!--css div popup start-->
    <a class="popup_link btn btn-xs btn-sg-pass" onfocus='this.blur();' href="javascript:showTestDetail('div_%(tid)s')">
        %(status)s
    </a>

    <div id='div_%(tid)s' class="popup_window">
        <div style='text-align: right;cursor:pointer'>
        <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
           [x]</a>
        </div>
        <pre>
        %(script)s
        </pre>
    </div>
    <!--css div popup end-->

    </td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_WITH_OUTPUT_TMPL_FAIL = r"""
    <tr id='%(tid)s' class='%(Class)s'>
        <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
        <td colspan='5' align='center'>

        <!--css div popup start-->
        <a class="popup_link btn btn-xs btn-sg-fail" 
           onfocus='this.blur();' 
           href="javascript:showTestDetail('div_%(tid)s')" >
           %(status)s
        </a>

        <div id='div_%(tid)s' class="popup_window">
            <div style='text-align: right;cursor:pointer'>
            <a onfocus='this.blur();' onclick="document.getElementById('div_%(tid)s').style.display = 'none' " >
               [x]</a>
            </div>
            <pre>
            %(script)s
            </pre>
        </div>
        <!--css div popup end-->

        </td>
    </tr>
    """  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_NO_OUTPUT_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>%(status)s</td>
</tr>
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""
%(output)s
"""
