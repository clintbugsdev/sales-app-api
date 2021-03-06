# Generated by Django 3.1.5 on 2021-02-06 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('unit_in_stock', models.FloatField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=4)),
                ('reorder_level', models.FloatField()),
                ('on_sale', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('categories', models.ManyToManyField(to='core.Category')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.unit')),
            ],
        ),
    ]
