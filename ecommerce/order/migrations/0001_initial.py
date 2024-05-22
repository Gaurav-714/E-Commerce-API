# Generated by Django 5.0.1 on 2024-05-20 23:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0006_alter_productreview_rating'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_amount', models.IntegerField(default=0)),
                ('area', models.CharField(default='', max_length=500)),
                ('city', models.CharField(default='', max_length=100)),
                ('state', models.CharField(default='', max_length=100)),
                ('country', models.CharField(default='', max_length=100)),
                ('zip_code', models.CharField(default='', max_length=100)),
                ('phone_no', models.CharField(default='', max_length=100)),
                ('payment_status', models.CharField(choices=[('Paid', 'Paid'), ('Unpaid', 'Unpaid')], default='Unpaid', max_length=20)),
                ('payment_mode', models.CharField(choices=[('COD', 'Cod'), ('CARD', 'Card')], default='COD', max_length=20)),
                ('order_status', models.CharField(choices=[('Processing', 'Processing'), ('Shipped', 'Shipped'), ('Deliverd', 'Deliverd')], default='Processing', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=200)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.DecimalField(decimal_places=2, max_digits=7)),
                ('image', models.CharField(default='', max_length=500)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orderItems', to='order.order')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
            ],
        ),
    ]
