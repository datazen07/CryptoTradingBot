import os
from datetime import datetime

import backtrader as bt
from django.conf import settings
from django.shortcuts import render

from .models import Chart
from .my_strategy import MyStrategy


def config_cerebro(symbol, start_date, end_date, percentage, length):
    data_name = symbol.upper() + '-USD'
    print(data_name)
    from_date = datetime(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:]))
    print(from_date)
    to_date = datetime(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:]))
    print(to_date)

    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(MyStrategy, maperiod=length)

    # Create a Data Feed
    data = bt.feeds.YahooFinanceData(dataname=data_name, fromdate=from_date, todate=to_date)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)

    # Set our desired cash start with a value of 100 000
    global cash_start
    cash_start = 100000
    cerebro.broker.setcash(cash_start)
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Add a PercentSize sizer
    cerebro.addsizer(bt.sizers.PercentSizer, percents=percentage)

    # 0.1% ... divide by 100 to remove the %
    cerebro.broker.setcommission(commission=0.001)

    # Run over everything
    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    global cash_end
    cash_end = round(cerebro.broker.getvalue(), 2)

    return cerebro


def index(request):
    chart_image_name = 'chart.png'
    context = {}

    if request.method == 'GET':
        pass
    else:  # request.method == 'POST'
        print(request.POST.get('crypto'),
              request.POST.get('start_date'),
              request.POST.get('end_date'),
              request.POST.get('length'),
              request.POST.get('percentage'))

        crypto = request.POST.get('crypto')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        length = int(request.POST.get('length'))
        percentage = int(request.POST.get('percentage'))

        figure = config_cerebro(crypto, start_date, end_date, percentage, length).plot(style='candlebars')[0][0]

        # Create a chart object model
        chart = Chart(image=chart_image_name)
        chart.save()
        # Update the image name
        chart.image = str(chart.pk) + chart_image_name
        chart.save()

        my_chart = os.path.join(settings.MEDIA_ROOT, str(chart.get_image()))

        figure.savefig(my_chart, bbox_inches="tight")

        context = {'chart': chart,
                   'cash_start': cash_start,
                   'crypto': crypto,
                   'start_date': start_date,
                   'end_date': end_date,
                   'length': length,
                   'percentage': percentage,
                   'cash_end': cash_end,
                   }

    return render(request, 'backtest/index.html', context)
