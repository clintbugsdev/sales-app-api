# Generated by Django 3.1.5 on 2021-02-13 16:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.FloatField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=12)),
                ('sub_total', models.DecimalField(decimal_places=2, max_digits=12)),
                ('required_date', models.DateField()),
                ('is_cancelled', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.product')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.supplier')),
            ],
        ),
    ]
