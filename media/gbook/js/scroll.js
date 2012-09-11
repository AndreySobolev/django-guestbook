function get(id)
{
    return document.getElementById(id);
}
	var scroller 	;
	var scrollBar 	;
	var container 	;
	var content 	;
	var scrollerTrackHeight ;
	var scrollerHeight ;
	var objectTrackHeight;
	var objectHeight ;
	var delta;
	var canDrag = false;
	var shift_x;  
	var shift_y;  

window.onload = (function (){
	if ((get('scroll')=='undefined')||(get('scroll')==null)) return;  
	scroller 	= get('scroller');
	scrollBar 	= get('scroll_bar');
	container = get('container');
	content 	= get('content');
	if (container.offsetHeight < content.offsetHeight) 
		scrollBar.style.display = "block";

	// Высота видимой части объекта 
	objectHeight  = container.offsetHeight; 

	// Высота  объекта целиком
	objectTrackHeight = content.offsetHeight; 

	//Высота прокрутки
	scrollerTrackHeight = scrollBar.offsetHeight;

	// На каждый пиксель сдвига бегунка мы будем сдвигать меню на величину delta
	delta = objectTrackHeight / scrollerTrackHeight;

	//Изменяем размер скролла
	scrollerHeight = Math.round ((objectHeight / objectTrackHeight ) *  scrollerTrackHeight);
	scroller.style.height = Math.round ((objectHeight / objectTrackHeight ) *  scrollerTrackHeight) + "px";

	// Учтем, что максимальная ширина ползунка - это ширина полосы прокрутки
	scrollerHeight = (scrollerHeight > scrollerTrackHeight) ?  scrollerTrackHeight : scrollerHeight;

	// Захватить
	scroller.onmousedown = drag;
	scrollBar.onmousedown = function (event){ blockEvent(event);  return false;}

	// Перетащить
	document.body.onmousemove = move;

	// Бросить
	document.body.onmouseup = drop;

	scroller.style.top = "0px"
	scroller.style.left = "0px"

  // Для Mozilla необходимо создать EventListener:
  if (content.addEventListener)
  {
      content.addEventListener('DOMMouseScroll', wheel, false);
  }
  // Для всех остальных браузеров подойдет вот такая инициализация:
  content.onmousewheel = wheel;
});


function blockEvent(event)
{
    if (!event)
    {
        event = window.event;
    }
    if(event.stopPropagation) event.stopPropagation();
    else event.cancelBubble = true;
    if(event.preventDefault) event.preventDefault();
    else event.returnValue = false;
}

function drag(event)
{
    if (!event)
    {
        event = window.event;
    }
    canDrag = true;
    shift_y = event.clientY - parseInt(scroller.style.top);
    shift_x = event.clientX - parseInt(scroller.style.left);
    blockEvent(event);
    return false;
}

function move(event)
{
    if (!event)
    {
        event = window.event;
    }
    // Здесь мы как раз и проверяем:
    // Сдвигать ли нам ползунок вслед за мышью, или оставить его неподвижным

    if ((canDrag)&&((event.clientX - shift_x) < 20)&&((event.clientX - shift_x) > -20)&&((event.button==1)||((event.button==0)&&(event.which==1))))
    {
        setPosition(event.clientY - shift_y);
    }
    return false;
}

function drop()
{
    // Освобождаем ползунок
    canDrag = false; 
}

function setPosition(newPosition)
{
    if ( (newPosition <= scrollerTrackHeight - scrollerHeight) && (newPosition >= 0) )
    {
        scroller.style.top = newPosition + "px";
    }
    else if (newPosition > scrollerTrackHeight  - scrollerHeight )
    {
        scroller.style.top = (scrollerTrackHeight  - scrollerHeight)  + "px";
    }
    else
    {
        scroller.style.top = 0 + "px";
    }
    // Вслед за ползунком передвинем меню:
    content.style.marginTop = Math.round( parseInt(scroller.style.top)  * delta * (-1) ) + "px";
    return false;
}

function wheel(event)
{
    // Переменная, в которой будем хранить сдвиг
    var wheelDelta = 0;
    
    // Шаг меню при прокрутке
    var step = 20;
    if (!event) 
    {
        event = window.event;
    }
    if (event.wheelDelta) 
    {
        // В IE и Opera при сдвиге колеса на один шаг event.wheelDelta принимает значение 120
        // Значения сдвига в этих двух браузерах совпадают по знаку.
        wheelDelta = -event.wheelDelta/120;
    } 
    else if (event.detail) 
    {
        // В Mozilla, значение wheelDelta отличается по знаку от значения в IE.
        // Сдвиг колеса на один шаг соответствует значению 3 параметра event.detail          
        wheelDelta = event.detail/3;
    }
    // При скроллинге вверх wheelDelta > 0
    // При скролинге вниз - wheelDelta < 0
    if (wheelDelta)
    {
        var currentPosition = parseInt(scroller.style.top);               
        var newPosition = wheelDelta*step + currentPosition;
        setPosition(newPosition); 
    }
    
    // Убиваем событие (чтобы страница не скроллилась)
    if (event.preventDefault)
    {
        event.preventDefault();
    }
    event.returnValue = false;
    blockEvent(event);
}


