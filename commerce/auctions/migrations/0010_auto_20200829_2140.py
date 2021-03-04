# Generated by Django 3.1 on 2020-08-30 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0009_auto_20200829_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auction',
            name='category_name',
            field=models.ManyToManyField(blank=True, related_name='auctions_with_category', to='auctions.Category'),
        ),
    ]
