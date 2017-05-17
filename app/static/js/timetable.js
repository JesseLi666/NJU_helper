var patt3 = new RegExp("morning");
var patt4 = new RegExp("afternoon");
var week_text = $('#week_choose').text();
var patt1 = new RegExp("[0-9]+");
var week_now = parseInt(patt1.exec(week_text))-1;

$(function () {
$("#week_choose").click(function(){
    $("#treelist_dummy").click();
});

$("#treelist").mobiscroll().treelist({
        theme: "mobiscroll",
        lang: "zh",
        display: 'modal',
        cancelText: null,
        defaultValue: [week_now],
        onSelect: function (valueText) { location.href=$SCRIPT_ROOT+'/timetable/'+(parseInt(valueText)+1); },
        headerText: function (valueText) { return "选择周数"; }
    });
});
$(document).ready(function () {
    $('div.course').click(function(){
        $('.modal-title').text('课程详情');
        var row_cnt;
        var col_cnt = $(this).parent().prevAll().length-1;
        if(patt3.test($(this).parent().attr("class"))){
            row_cnt = $(this).prevAll().length;
        }
        else if(patt4.test($(this).parent().attr("class"))){
            row_cnt = $(this).prevAll().length+4;
        }
        else{
            row_cnt = $(this).prevAll().length+8;
        }
        $('div.modal-body').remove();

        for(var i=0; i<courses[col_cnt][row_cnt][1].length; i++){
            index = courses[col_cnt][row_cnt][1][i];
            $('div.modal-footer').before('<div class="modal-body">'+'<p>课程编号: '+message[index][3]+'<br>课程名称: '+message[index][0]+'<br>教师: '+message[index][1]+'<br>选课类型: '+message[index][4]+'<br>校区: '+message[index][5]+'<br>上课地点及时间: <br>'+message[index][2]+'</p>'+'</div>');
        }

        $('#myModal').modal('show');
    });
    $('tr.course_except').click(function () {
        $('.modal-title').text('课程详情');
        $('div.modal-body').remove();
        index = $(this).children().last().text();
        $('div.modal-footer').before('<div class="modal-body">'+'<p>课程编号: '+message[index][3]+'<br>课程名称: '+message[index][0]+'<br>教师: '+message[index][1]+'<br>选课类型: '+message[index][4]+'<br>校区: '+message[index][5]+'<br>上课地点及时间: <br>'+message[index][2]+'</p>'+'</div>');
        $('#myModal').modal('show');
    })

})/**
* Created by Li on 2017/2/28.
*/


