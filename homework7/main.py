import matplotlib.pyplot as plt
import numpy as np
import requests
from datetime import datetime
from constants import *


def make_calendars_dates(dates):
    return [datetime.strptime(date_str, '%Y-%m-%d').strftime('%d %b') for date_str in dates]
    # days = [datetime.strptime(date_str, '%Y-%m-%d') for date_str in dates]
    # return [date.strftime('%d %b') for date in days]


def get_average_for_each_day(numbers):
    return [round(sum(numbers[i:i + 24]) / 24, 2) for i in range(0, len(numbers), 24)]


def get_data(city_latitude, city_longitude, hourly=(), forecast_days=7, daily=()):
    """
    Fetch weather data from the Open Meteo API for a specified city.

    Args:
        city_latitude (str): The latitude of the city for which you want to fetch weather data.
        city_longitude (str): The longitude of the city for which you want to fetch weather data.
        hourly (tuple): The type of hourly weather data to fetch (e.g., 'temperature_2m', 'rain').
        forecast_days (int): The number of forecast days to retrieve.
        daily (tuple): A tuple of additional daily weather data types to fetch. (e.g., 'rain_sum', 'temperature_2m_max',
         'temperature_2m_min')

    Returns:
        dict: A JSON response containing weather data.

    Note:
        This function sends an HTTP GET request to the Open Meteo API with the specified parameters and returns the
        response as JSON data. If there is an error in fetching data, it prints an error message and returns None.

    Example:
        To fetch hourly temperature data for the next 7 days and additional daily data for rain, use:
        get_data('city_latitude', 'city_longitude', ('temperature_2m',), 7, ('rain',))
    """
    url = f'{BASE_URL}latitude={city_latitude}&longitude={city_longitude}&hourly={",".join(hourly)}&forecast_days=' \
          f'{forecast_days}&daily={",".join(daily)}&timezone=auto'
    response = requests.get(url)
    if response.status_code != 200:
        print("Error fetching data. Status code:", response.status_code)
    return response.json()


def draw_line_chart(forecast_days):
    data = get_data(UZH_CITY_LATITUDE, UZH_CITY_LONGITUDE, (HOURLY_TEMPERATURE,), forecast_days,
                    (DAILY_TEMP_MAX, DAILY_TEMP_MIN))
    hourly_temperatures = data['hourly']['temperature_2m']
    daily_average_temperatures = get_average_for_each_day(hourly_temperatures)

    x_ticks = np.arange(forecast_days * 24)
    y_ticks = np.arange(0, 31, 5)
    fig, ax = plt.subplots(figsize=(12, 6))

    # max_temperatures = [max(hourly_temperatures[i:i + 24]) for i in range(0, len(hourly_temperatures), 24)]
    # min_temperatures = [min(hourly_temperatures[i:i + 24]) for i in range(0, len(hourly_temperatures), 24)]
    max_temperatures = data['daily'][DAILY_TEMP_MAX]
    min_temperatures = data['daily'][DAILY_TEMP_MIN]
    # np.interp()

    ax.plot(hourly_temperatures, label='Hourly Temp', linestyle='--', markersize=5, linewidth=1)
    ax.plot(range(0, len(hourly_temperatures), 24), daily_average_temperatures, label='Daily Avg Temp', linestyle='-',
            marker='s', markersize=5, linewidth=1)
    ax.plot(range(0, len(hourly_temperatures), 24), max_temperatures, label='Max Temp', linestyle='-.',
            markersize=5, linewidth=3)
    ax.plot(range(0, len(hourly_temperatures), 24), min_temperatures, label='Min Temp', linestyle=':', marker='v',
            markersize=5, linewidth=2)

    ax.set_xticks(x_ticks[::24])
    ax.set_yticks(y_ticks)
    ax.set_xticklabels(make_calendars_dates(data['daily']['time']))
    ax.set_yticklabels(y_ticks)
    ax.set_ylabel('Temperature (°C)')
    ax.set_title(f'Temperature in Uzhorod for the Last 16 DAYS')
    ax.legend()

    plt.savefig('temperature_chart1.png')
    plt.show()


def draw_bar_chart(forecast_days):
    bar_width = 0.2
    days = range(1, forecast_days + 1)

    data_a_city = get_data(KHARKIV_CITY_LATITUDE, KHARKIV_CITY_LONGITUDE, (HOURLY_RAIN,), forecast_days,
                           (DAILY_RAIN_SUM,))
    data_b_city = get_data(KYIW_CITY_LATITUDE, KYIW_CITY_LONGITUDE, (HOURLY_RAIN,), forecast_days, (DAILY_RAIN_SUM,))
    data_c_city = get_data(UZH_CITY_LATITUDE, UZH_CITY_LONGITUDE, (HOURLY_RAIN,), forecast_days, (DAILY_RAIN_SUM,))

    rain_sum_mm_a = [day for day in data_a_city['daily'][DAILY_RAIN_SUM]]
    rain_sum_mm_b = [day for day in data_b_city['daily'][DAILY_RAIN_SUM]]
    rain_sum_mm_c = [day for day in data_c_city['daily'][DAILY_RAIN_SUM]]

    plt.bar([day - bar_width for day in days], rain_sum_mm_a, bar_width, color='b', label='Kharkiv')
    plt.bar(days, rain_sum_mm_b, bar_width, color='g', label='Kyiw')
    plt.bar([day + bar_width for day in days], rain_sum_mm_c, bar_width, color='r', label='Uzhorod')

    plt.ylabel('Rain Sum (mm)')
    plt.title('Daily Rain Sum for Each City')
    plt.xticks(days, make_calendars_dates(data_a_city['daily']['time']))
    plt.legend()
    plt.savefig('rain_sum_chart1.png')
    plt.show()


def draw_pie_chart(forecast_days):
    data = get_data(UZH_CITY_LATITUDE, UZH_CITY_LONGITUDE,
                    (HOURLY_CLOUDCOVER_LOW, HOURLY_CLOUDCOVER_MID, HOURLY_CLOUDCOVER_HIGH), forecast_days)

    average_cloudcover_low = get_average_for_each_day(data['hourly'][HOURLY_CLOUDCOVER_LOW])
    average_cloudcover_mid = get_average_for_each_day(data['hourly'][HOURLY_CLOUDCOVER_MID])
    average_cloudcover_high = get_average_for_each_day(data['hourly'][HOURLY_CLOUDCOVER_HIGH])

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    labels = ['Cloudcover Low', 'Cloudcover Mid', 'Cloudcover High']
    days = make_calendars_dates(data['daily']['time'])
    fig.suptitle('Cloudcover Low, Cloudcover Mid and Cloudcover High for last three days')

    for i in range(3):
        # Create a pie chart for each day
        sizes = [average_cloudcover_low[i], average_cloudcover_mid[i], average_cloudcover_high[i]]

        axes[i].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=30 * i, shadow=True, explode=(.1, 0, 0),
                    wedgeprops={'edgecolor': 'black'})
        axes[i].set_title(days[i])

    plt.tight_layout()
    plt.savefig('pie_chart.png')
    plt.show()


def draw_histogram(forecast_days):
    data = get_data(UZH_CITY_LATITUDE, UZH_CITY_LONGITUDE, (HOURLY_WINDSPEED,), forecast_days)
    x = data['hourly'][HOURLY_WINDSPEED]

    fig, ax = plt.subplots()

    ax.hist(x, bins=8, edgecolor='k', alpha=0.7)
    ax.set_title(f'Hourly wind speed data for Uzhhorod for {forecast_days} days')
    ax.set_ylabel('?')
    ax.set_xlabel('Windspeed (m/s)')
    plt.savefig('histogram.png')
    plt.show()


def draw_scatter_plot(dim=2):
    """
    Generate a 2D or 3D scatter plot based on the specified dimension.

    Parameters:
        dim (int): The dimension of the scatter plot, either 2 or 3.
            If dim is 2, it will create a 2D scatter plot of Temperature vs. Cloudcover.
            If dim is 3, it will create a 3D scatter plot of Temperature vs. Cloudcover vs. Humidity.
    """
    data = get_data(UZH_CITY_LATITUDE, UZH_CITY_LONGITUDE,
                    (HOURLY_TEMPERATURE, HOURLY_WINDSPEED, HOURLY_CLOUDCOVER, HOURLY_PRECIPITATION, HOURLY_HUMIDITY), 7)

    temperature = data['hourly'][HOURLY_TEMPERATURE]
    cloudcover = data['hourly'][HOURLY_CLOUDCOVER]
    wind_speed = data['hourly'][HOURLY_WINDSPEED]
    humidity = data['hourly'][HOURLY_HUMIDITY]
    precipitation = data['hourly'][HOURLY_PRECIPITATION]

    plt.figure(figsize=(10, 6))

    # Отмечаем точки как треугольники, если есть осадки
    is_precipitation = [p > 0 for p in precipitation]
    marker_size = np.array(wind_speed) * 4

    if dim == 2:
        for cc, temp, ws, rh, precip in zip(cloudcover, temperature, marker_size, humidity, is_precipitation):
            marker = '^' if precip else 'o'
            plt.scatter(cc, temp, s=ws, c=rh, edgecolors='black', alpha=0.75, marker=marker)

        cbar = plt.colorbar()
        cbar.set_label('humidity')
        plt.xlabel('Cloudcover Total')
        plt.ylabel('Temperature (2 m)')
        plt.title('Scatter Plot of Temperature vs. Cloudcover')
        plt.savefig('scatter.png')

    elif dim == 3:
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')

        for cc, temp, ws, rh, precip in zip(cloudcover, temperature, marker_size, humidity, is_precipitation):
            marker = '^' if precip else 'o'
            ax.scatter(cc, temp, rh, s=ws, c='b' if precip else 'r', edgecolors='black', alpha=0.75, marker=marker)

        ax.set_xlabel('Cloudcover Total')
        ax.set_ylabel('Temperature (2 m)')
        ax.set_zlabel('Humidity')
        ax.set_title('3D Scatter Plot of Temperature vs. Cloudcover vs. Humidity')
        plt.savefig('scatter3d.png')

    plt.show()


if __name__ == "__main__":
    draw_line_chart(16)
    draw_bar_chart(7)
    draw_pie_chart(3)
    draw_histogram(7)
    draw_scatter_plot()
    draw_scatter_plot(3)
