$(document).ready({
    var name = $('#name');
    var type = $('#type');
    var weight = $('#weight');
    var grade = $('#grade');
    var arr = ['通修', '平台', '核心'];

    $('#resultButton').click(function () {
        var g = new Array();
        var ch = $('#choose:checked');
        if (ch.length === 0) return;
        ch.each(function () {
            var t_w = $(this).parents("tr").find("span#weight").first().text();
            var t_g = $(this).parents("tr").find("span#grade").first().text();
            g.push([t_w, t_g])
        });
        $.ajax({
            type:'post',
            traditional:true,
            url:$SCRIPT_ROOT+'/_cal',
            data:{'g':g},
            success:function (data) {
                alert('您选中的课程计算的GPA为：'+data)
            }
        });
        }

    );

    $('#resultButton2').click(function () {
        var g = new Array();
        var ch = $('#choose:checked');
        if (ch.length === 0) return;
        ch.each(function () {
            var t_w = $(this).parents("tr").find("span#weight").first().text();
            var t_g = $(this).parents("tr").find("span#grade").first().text();
            g.push([t_w, t_g])
        });
        $.ajax({
            type:'post',
            traditional:true,
            url:$SCRIPT_ROOT+'/_cal2',
            data:{'g':g},
            success:function (data) {
                alert('您选中的课程经标准算法计算得到的GPA为：'+data)
            }
        });
        }

    );

    $('#resultButton3').click(function () {
        var g = new Array();
        var ch = $('#choose:checked');
        if (ch.length === 0) return;
        ch.each(function () {
            var t_w = $(this).parents("tr").find("span#weight").first().text();
            var t_g = $(this).parents("tr").find("span#grade").first().text();
            g.push([t_w, t_g])
        });
        $.ajax({
            type:'post',
            traditional:true,
            url:$SCRIPT_ROOT+'/_cal3',
            data:{'g':g},
            success:function (data) {
                alert('您选中的课程经WES算法计算得到的GPA为：'+data)
            }
        });
        }

    );

    var choose = $('input#choose');
    $("#checkall").click(
        function(){
            choose = $('input#choose');
            var allChecked = choose.filter(':checked').length === choose.length;
            // alert(allChecked)
            if(allChecked == true){
                choose.prop('checked', false)
            }else{
                choose.prop('checked', true)
            }
        }
    );
    $('#SelectAll').click(function () {
        choose.prop('checked', true)
    });

    $('#disSelectAll').click(function () {
        choose.prop('checked', false)
    });
    $('#invertSelect').click(function () {
        choose = $('input#choose');
        choose.each(function () {
            $(this).prop('checked', !$(this).prop('checked'));
        })
    });
    $('#someSelect').click(function () {
        choose = $('input#choose');
        choose.each(function () {
            t = $(this).parents("tr").find("span#type").first().text();
            g = $(this).parents("tr").find("span#grade").first().text();
            if ($.inArray(t, arr) !== -1 && g != 0){
                $(this).prop('checked', true);
            }
            else{
                $(this).prop('checked', false);
            }
        });
    });
    var i=0;
    $('#add_do').click(function () {
        a=$(this).parent().find("input#add_weight").first();
        b=$(this).parent().find("input#add_grade").first();
        if(a.val()!=0 && b.val()!=0){
            i+=1;
            str="<tr><td align=\"center\"><span id=\"name\">新增课程"+i+"</span></td><td align=\"center\"><span id=\"type\">新增</span></td>"+
                "<td align=\"center\"><span id=\"weight\">"+a.val()+"</span></td><td align=\"center\"><span id=\"grade\">"+
                b.val()+"</span></td>"+"<td align=\"center\"><input type=\"checkbox\" id=\"choose\" checked></td></tr>";
            $('tbody#new_courses').append(str);
            a.val(null);
            b.val(null);
        }
        else {
            alert('请输入成绩和学分！')
        }

    });
    $('tbody#term:odd').css('background','#f1fafa');
    $('tbody#term:even').css('background','#e8e8ff');
    // $(' #whathappened').hide();
    // $(' #whathappened').css('background-color','#B2E0FF');
    // getElementById(" whathappened").css('background-color','#B2E0FF');
    // $("div").css('background-color','#B2E0FF');
    // $("tr:odd").css("background-color","#B2E0FF");
});


