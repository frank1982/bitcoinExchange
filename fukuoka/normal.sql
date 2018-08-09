create table actualPriceRecord(
id int not null primary key auto_increment,
queryTime varchar(56),
symbol varchar(56),
tradeDirection varchar(56),
tradeRate float,
sellMarketNumber float,
buyMarketNumber float
);
create table tradeLimit(
id int not null primary key auto_increment,
symbol varchar(56),
bianSell_huobiBuy float,
huobiSell_bianBuy float
);
create table symbols(
id int not null primary key auto_increment,
symbol varchar(56),
usable int
);
create table priceData(
id int not null primary key auto_increment,
queryTime varchar(56),
rate_huobiSell_bianBuy float(9,6),
rate_bianSell_huobiBuy float(9,6),
lowestSellPrice_huobi  float(9,6),
highestBuyPrice_huobi  float(9,6),
lowestSellNum_huobi  float(9,6),
highestBuyNum_huobi  float(9,6),
lowestSellPrice_bian  float(9,6),
highestBuyPrice_bian  float(9,6),
lowestSellNum_bian  float(9,6),
highestBuyNum_bian  float(9,6),
symbol varchar(56)
);
insert into symbols (symbol,usable)
values ('EOSUSDT',0);

insert into tradeLimit(symbol,bianSell_huobiBuy,huobiSell_bianBuy) 
values ('STEEMETH',0.001,0.001);
select * from tradeLimit;
select * from symbols where usable >= 100;
select * from priceData;
select * from symbols;

