#统计出现次数
select symbol, count(*) from priceData group by symbol;
delete from priceData where id >= 0;
select * from priceData order by id desc;

select * from symbols;
select * from symbols where usable>=100;