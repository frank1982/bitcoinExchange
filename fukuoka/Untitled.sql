
create table symbols_train(
id int not null primary key auto_increment,
symbol varchar(56) not null unique
);

insert into symbols_train (symbol) values 
('BCD_BTC'),
('ETH_BTC'),
('BCH_BTC'),
('LTC_BTC'),
('DASH_BTC'),
('ETC_BTC'),
('XRP_BTC'),
('BTG_BTC'),
('QTUM_BTC'),
('BCH_USDT'),
('ETH_USDT'),
('LTC_USDT');

select * from symbols_train;

create table price_train(
id int not null primary key auto_increment,
symbol varchar(56) not null,
findTime varchar(56),
price_bianSell_substract_huobiBuy float(24,8),
price_huobiSell_substract_bianBuy float(24,8),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

select * from price_train;


create table balance(
id int not null primary key auto_increment,
balance_targetCoin_bian float(24,8),
balance_baseCoin_bian float(24,8),
balance_targetCoin_huobi float(24,8),
balance_baseCoin_huobi float(24,8),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

select * from balance;

create table balance_normal(
id int not null primary key auto_increment,
miner varchar(100),
targetCoin varchar(100),
baseCoin varchar(100),
balance_targetCoin_bian float(24,8),
balance_baseCoin_bian float(24,8),
balance_targetCoin_huobi float(24,8),
balance_baseCoin_huobi float(24,8),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
select * from balance_normal;


create table profit(
id int not null primary key auto_increment,
targetCoinChanged float(24,8),
baseCoinChanged float(24,8),
basePrice float(24,8),
result float(5,2),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

create table tradeCoins(
id int not null primary key auto_increment,
targetCoin varchar(56),
baseCoin varchar(56),
limitRate_huobiSell_bianBuy float(5,2),
limitRate_bianSell_huobiBuy float(5,2),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);



insert into tradeCoins (targetCoin,baseCoin,limitRate_huobiSell_bianBuy,
limitRate_bianSell_huobiBuy) values ('DASH','BTC',0.3,0.3);
select * from tradeCoins;


create table lottery_tb(
id int not null primary key auto_increment,
employeeID varchar(56),
employeeName varchar(56),
lotteryStatus int,
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
select * from lottery_tb;
select count(*) from lottery_tb order by id desc;
delete from lottery_tb;
select id from lottery_tb where lotteryStatus=0;
select count(*) from lottery_tb where lotteryStatus=1;
select employeeID from lottery_tb;
select employeeID,employeeName from lottery_tb;
select employeeID,employeeName from lottery_tb limit 924,1;


create table rateRecord_xrpbtc_huobi_bian(
id int not null primary key auto_increment,
queryTime varchar(56),
rate_huobiSell_bianBuy float(9,6),
rate_bianSell_huobiBuy float(9,6),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);



create table tradeCoins_multiple(
id int not null primary key auto_increment,
targetCoin varchar(56),
baseCoin varchar(56),
limitRate_huobiSell_bianBuy float(5,2),
limitRate_bianSell_huobiBuy float(5,2),
player varchar(56),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);
 insert into tradeCoins_multiple (targetCoin,baseCoin,limitRate_huobiSell_bianBuy,
 limitRate_bianSell_huobiBuy,player) values ('LTC','USDT',0.5,0.5,'kamakura');
SELECT * FROM tradeCoins_multiple;

create table rateRecord_btcusdt_huobi_bian(
id int not null primary key auto_increment,
queryTime varchar(56),
rate_huobiSell_bianBuy float(9,6),
rate_bianSell_huobiBuy float(9,6),
update_time timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

SET SQL_SAFE_UPDATES=0; 
SELECT * FROM tradeCoins_multiple;

delete from rateRecord_ltcusdt_huobi_bian;

#记录数
select count(*) from rateRecord_ltcusdt_huobi_bian;
select count(*) from rateRecord_ltcusdt_huobi_bian where rate_huobiSell_bianBuy > 0.6;
select count(*) from rateRecord_ltcusdt_huobi_bian where rate_bianSell_huobiBuy > 0.6;
#详细记录
select * from rateRecord_ltcusdt_huobi_bian where rate_bianSell_huobiBuy > 0 order by id desc;
select * from rateRecord_ltcusdt_huobi_bian order by id desc;
#最大值
select max(rate_huobiSell_bianBuy) from rateRecord_ltcusdt_huobi_bian;
select max(rate_bianSell_huobiBuy) from rateRecord_ltcusdt_huobi_bian;
#最大的那条记录
select * from rateRecord_ltcusdt_huobi_bian where rate_bianSell_huobiBuy > 1.8;
#平均值
SELECT AVG(rate_huobiSell_bianBuy) AS av FROM rateRecord_ltcusdt_huobi_bian where rate_huobiSell_bianBuy > 0.6;
SELECT AVG(rate_bianSell_huobiBuy) AS av FROM rateRecord_ltcusdt_huobi_bian where rate_bianSell_huobiBuy > 0.6;



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

create table symbols(
id int not null primary key auto_increment,
symbol varchar(56),
usable int
);

create table tradeLimit(
id int not null primary key auto_increment,
symbol varchar(56),
bianSell_huobiBuy float,
huobiSell_bianBuy float
);

create table actualPriceRecord(
id int not null primary key auto_increment,
queryTime varchar(56),
symbol varchar(56),
tradeDirection varchar(56),
tradeRate float,
sellMarketNumber float,
buyMarketNumber float
);

select * from tradeLimit;
#'STEEMETH':{'bianSell_huobiBuy':0.4,'huobiSell_bianBuy':0.1}
insert into tradeLimit(symbol,bianSell_huobiBuy,huobiSell_bianBuy) 
values ('STEEMETH',0.001,0.001);
select * from actualPriceRecord order by id desc;
select count(*) from actualPriceRecord;
delete from actualPriceRecord where id >= 1;

SET SQL_SAFE_UPDATES=0; 
delete from priceData where id >= 1;
delete from priceData where rate_huobiSell_bianBuy<0.5 and rate_bianSell_huobiBuy<0.5;
select count(*) from priceData;
SELECT symbol,count(*) as num FROM priceData group BY symbol order by num desc;
select * from priceData order by id asc;
select * from priceData where symbol="EOSUSDT" order by id desc;
select count(*) from priceData where symbol="EOSUSDT" and rate_bianSell_huobiBuy>1;
select count(*) from priceData where symbol="EOSUSDT" and rate_huobiSell_bianBuy>-0.5;
select * from priceData where symbol="EOSUSDT" order by id desc;
select * from symbols where usable >= 100;
select * from symbols where usable < 100;
select * from symbols where usable = 2;
select * from symbols where usable = 1;
select * from symbols;
select * from symbols where usable >=20 and usable <=30;
select * from symbols where usable <20;
