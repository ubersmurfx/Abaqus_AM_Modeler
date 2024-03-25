# Abaqus_AM_Modeler
Plug-in Additive Manufacturing in Abaqus CAE

Для созданиия серии событий из GCode может использоваться следующий скрипт:
```
abaqus python generateEventSeries.py <name of GCode file>.gcode <nameroller_pad_dimension> <delay_between_layers> <power>
```
Для примера:
```
abaqus python generateEventSeries.py 5.gcode 0.0 10 1000
```

Specifying Progressive Element Activation
Вы можете смоделировать осаждение шарика исходного материала из движущегося сопла, используя активацию прогрессивного элемента в структурном или термическом анализе. Высота, ширина и ориентация прямоугольного сечения валика осажденного сырья могут меняться со временем.
![image](https://github.com/Ubersmurf2010/Abaqus_AM_Modeler/assets/113335397/48cfb460-1a75-41ca-a565-8fee2cbae692)
