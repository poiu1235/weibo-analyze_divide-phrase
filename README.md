# weibo-analyze_divide-phrase
put weibo-catcher content,tag,remark into jieba divide phrase system

and put result store into database(mysql and mongodb),

in fact, this step is arranging for next vital step(data mining).

to be honest, jieba system is really really nice,especially in chinese divide-phrase system,

its amazing performance and easy to used make me feel very surprise.

send best regard to the author.

------------------------------------------------------------------------
this time, you must adjust my "weibo-catch" program.(another project in my github)

there are create db code. if you want to use this code,

you must ensure that project can run in your computer fluent.

and ensure that your db have content in appropriate field.


---------------------------------------------------------------------------------------------------------
you need create a file named 'localconfig' used to record the account information and its format like follows:

[weibo]

weibouser=xxxxxxxx

weibopwd=xxxxxxxx

[db]

dbsite=xxxxxxxx

dbuser=xxxxxxxx

dbpwd=xxxxxxxx

[email]

emailuser=xxxxxxxx

emailpwd=xxxxxxxx

emailhost=smtp.163.com #xxxxxxxx

emailrec=xxxxxxxx

-------------------------------------
