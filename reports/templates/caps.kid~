<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:py="http://purl.org/kid/ns#"
      py:extends="'master.kid'">
<head>
<meta content="text/html; charset=utf-8"
      http-equiv="Content-Type" py:replace="''"/>
<title> ${name} - NeoWiki </title>

<script language="javascript">
  window.addEventListener('load', init, true);

  function init() {
    document.addEventListener('click', permClicked, true);
  }

  function setPerm(name, perm, set, on){
    document.debug.text.value = name + " " + perm + " " + set + " " + on + "\n"
    var value;
    if (on)
      value = "None";
    else
      value = set ? "True" : "False";
          
    var request = new XMLHttpRequest(); 
	  request.open("get", "?op=changePermission;link="+name+";permission="+perm+";value="+value, false); 
	  request.send(null);
    return request.status == 200
	}
	
  function permClicked(e) {
    var node = e.target;
    while(node.nodeType != node.ELEMENT_NODE){
      node = node.parentNode;
    }    
    var target = node.className.split(' ');

    if (target[0] == 'perm') {
      var set = target[1] == 'set'
      
      var on = target[2] == 'on'
      var perm = target[3]
      var link = target[4]
      if (on){
        if (setPerm(link, perm, set, on)){
          node.className = "perm "+ (set ? 'set':'unset') +" off "+perm + " " + link;
        }
      } else {
        if (setPerm(link, perm, set, on)){  
          var sibling = node
          while(sibling = sibling.nextSibling){
            if (typeof sibling.className == "undefined")            
              continue
            var class_ = sibling.className.split(' ')
            if (class_[0] == 'perm')
              sibling.className = "perm "+class_[1]+" off " + perm + " " + link;
          }
          var sibling = node
          while(sibling = sibling.previousSibling){
            if (typeof sibling.className == "undefined")            
              continue
            var class_ = sibling.className.split(' ')
            if (class_[0] == 'perm')
              sibling.className = "perm "+class_[1]+" off " + perm + " " + link;        
          }

          node.className = "perm "+ (set ? 'set':'unset') +" on "+perm + " " + link;      
        }
      }
    }
  

  }
</script>
</head> 
<body>
    <form style="display: none" name="debug"><textarea name="text" style="width:95%"  /></form>
    <div id="main_content">
      <table border="0" >
        <tr><td></td><td py:for="permission in permissions">${permission}</td></tr>
        <tr py:for="name in sorted(links)" class="operations" >
          <div class="permissions">
            <td>${'/'.join(map(str, links[name][0]))}<div class="id">${name}</div></td>
            <td py:for="permission in permissions">
                <div class="perm set ${'on' if links[name][1].get(permission, None) == True else 'off'} ${permission} ${name}"/>
                <div class="perm unset ${'on' if links[name][1].get(permission, None) == False else 'off'} ${permission} ${name}"/>
            </td>
          </div>
        </tr>
      </table>      
    </div>
</body>
</html>



