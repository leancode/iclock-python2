﻿// -*- coding: utf-8 -*-
___f = function () {
    jQuery.validator.messages.required = "必填";
    jQuery.validator.messages.email = "不是一个email地址";
    jQuery.validator.messages.date = "请输入一个合法的日期：yyyy/mm/dd";
    jQuery.validator.messages.dateISO = "请输入一个合法的 (ISO)日期：yyyy-mm-dd";
    jQuery.validator.messages.number = "请输入一个合法的数值.";
    jQuery.validator.messages.digits = "只能输入数字";
    jQuery.validator.messages.equalTo = "不一致";
    jQuery.validator.messages.minLength = String.format("最少{0}个字符");
    jQuery.validator.messages.maxLength = String.format("最多{0}个字符");
    jQuery.validator.messages.rangeLength = String.format("必须是{0}到{1}个字符之间");
    jQuery.validator.messages.rangeValue = String.format("必须是{0}到{1}之间的值");
    jQuery.validator.messages.maxValue = String.format("请输入一个不大于 {0} 的值");
    jQuery.validator.messages.minValue = String.format("请输入一个不小于 {0} 的值.");
    jQuery.validator.messages.xPIN = "只能输入数字或字母。";
    jQuery.validator.messages.xNum = "只能输入数字。";
    jQuery.validator.messages.xMobile = "手机号输入不正确。";
    jQuery.validator.messages.xTele = "座机号不正确。";
    jQuery.validator.messages.xSQL = "不能输入\"或\'。"
};
___f();

if (typeof(catalog) == "undefined") {
    catalog = {}
}
catalog['6 a.m.'] = '\u4e0a\u53486\u70b9';
catalog['Add'] = '\u589e\u52a0';
catalog['Available %s'] = '\u53ef\u7528 %s';
catalog['Calendar'] = '\u65e5\u5386';
catalog['Cancel'] = '\u53d6\u6d88';
catalog['Choose a time'] = '\u9009\u62e9\u4e00\u4e2a\u65f6\u95f4';
catalog['Choose all'] = '\u5168\u9009';
catalog['Chosen %s'] = '\u9009\u4e2d\u7684 %s';
catalog['Clear all'] = '\u6e05\u9664\u5168\u90e8';
catalog['Clock'] = '\u65f6\u949f';
catalog['January February March April May June July August September October November December'] = '\u4e00\u6708 \u4e8c\u6708 \u4e09\u6708 \u56db\u6708 \u4e94\u6708 \u516d\u6708 \u4e03\u6708 \u516b\u6708 \u4e5d\u6708 \u5341\u6708 \u5341\u4e00\u6708 \u5341\u4e8c\u6708';
catalog['Midnight'] = '\u5348\u591c';
catalog['Noon'] = '\u6b63\u5348';
catalog['Now'] = '\u73b0\u5728';
catalog['Remove'] = '\u5220\u9664';
catalog['S M T W T F S'] = '\u65e5 \u4e00 \u4e8c \u4e09 \u56db \u4e94 \u516d';
catalog['Select your choice(s) and click '] = '\u9009\u62e9\u5e76\u70b9\u51fb ';
catalog['Sunday Monday Tuesday Wednesday Thursday Friday Saturday'] = '\u661f\u671f\u65e5 \u661f\u671f\u4e00 \u661f\u671f\u4e8c \u661f\u671f\u4e09 \u661f\u671f\u56db \u661f\u671f\u4e94 \u661f\u671f\u516d';
catalog['Today'] = '\u4eca\u5929';
catalog['Tomorrow'] = '\u660e\u5929';
catalog['Yesterday'] = '\u6628\u5929';

catalog['Selected:'] = '已选择';
catalog['Select'] = '选择';
catalog['All'] = '全选';
catalog['None'] = '全不选';
catalog['Delete'] = '删除';
catalog['Operating failed for {0} !'] = '对选择的 {0} 进行操作失败！';
catalog['No Data {0}'] = '没有 {0} 数据，请添加！';
catalog['Please Select {0}: '] = '    请选择 {0}: ';
catalog['Loading Data {0}'] = '正在加载 {0} 数据...';
catalog['Select the range of time'] = '选择时间范围';
catalog['Start Time:'] = '起始时间：';
catalog['End Time:'] = '结束时间：';
catalog['(total {0})'] = '(总 {0})';
catalog['total {0}'] = '总 {0}';
catalog['none'] = '无';
catalog['Page:'] = '分页:';
catalog['Operation'] = '操作';
catalog['Please Select {1} to {0}'] = '请先选择要 {0} 的 {1} ！';
catalog['{1} disallowed for {0}!'] = '不能对所选择的 {0} 进行 {1}！';
catalog['Will {2} the {0} {1} ?'] = '将对如下 {0} {1} 进行 {2} ?';
catalog['Please Confirm!'] = '请予以确认！';
catalog['{1} selected {0} failed!'] = '对选择的 {0} 进行 {1} 失败！';
catalog['--- select ---'] = '--- 请选择 ---';
catalog['FP'] = '指纹数';
catalog['Please Input'] = '请输入';
catalog['Filter by {0}'] = '由 {0} 过滤';
catalog['None'] = '无';
catalog['department'] = '部门';
catalog['device'] = '设备';
catalog['employee'] = '使用人员';
catalog['user'] = '系统用户';
catalog.Submit = '提交';
catalog.Cancel = '取消';
catalog['Input the range of time:'] = '输入时间范围';
catalog['Order Asc'] = '按升序排列';
catalog['Order Desc'] = '按降序排列';
catalog['No Order'] = '不排序';
catalog['Are you sure initialize system？'] = '你确定要初始化系统吗？';
catalog['Shift Data for AC Time'] = '考勤时间设定数据';
catalog['Attendance Checking Exception Records'] = '考勤例外记录';
catalog['AC Clock-in/out Records'] = '考勤签到记录';
catalog['Department'] = '部门';
catalog['Employee'] = '人员';
catalog['Click the department to show the employees!'] = '单击部门显示该部门的所有人员';
catalog['Click the employee to show the employee shift details!'] = '选中一个人员和输入日期范围，查询排班详情';
catalog['Are you sure submit,it will delete all the temporary shifts between the dates you selected'] = '你确定要提交吗？提交后将把所选择的人员所在该时间范围内的所有临时排班都删除';
catalog['Are you sure delete the time-table?'] = '确定删除该时段吗？';
catalog['Select All'] = "全选";
catalog["Collaspe"] = "折叠";
catalog["Expand"] = "展开";
catalog["Refresh"] = "刷新";
catalog["Select Department"] = "选择部门";
catalog["Contain Children"] = "选择时包含下级部门";
catalog["Must select a device!"] = "必须选择一个设备";
catalog["Select None"] = "全不选";
catalog["Must select a device!"] = "必须选择一个设备";
catalog["Must input a valid date!"] = "必须输入合法的日期";
catalog["Clear pictures in device"] = "清除设备上的考勤照片";
catalog["show count:"] = "显示数量：";
